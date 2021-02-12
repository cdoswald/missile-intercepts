"""KMLTrajectorySim and KMLCamera classes."""
#TODO: Add stylemap (in utils)
#TODO: Add camera classes
#TODO: Add converter classes?

# Import packages
from datetime import datetime, timedelta
import inspect
import os
import sys
from typing import Optional

import pandas as pd

import simplekml

# Import local modules
script_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.join(script_dir, 'Utils'))
import geo_utils as geo
import kml_utils

# Define classes
class KMLTrajectorySim():
    """Base class for simulating a missile trajectory in KML.
    
    Attributes
        altkm_colname: column name in data indicating altitude (kilometers)
        bearingdeg_colname: column name in data indicating bearing (degrees)
        collada_model_link: path or URL to 3D model in COLLADA format (.dae)
        collada_model_scale: scale factor for all 3D model axes (x, y, and z)
        data: pandas DataFrame containing trajectory data
        kml_time_format: string format for KML timestamps/timespans
        kml: simplekml document containing KML data
        latdeg_colname: column name in data indicating latitude (degrees)
        launch_time: date and time of missile launch
        londeg_colname: column name in data indicating longitude (degrees)
        sim_end_time: simulation end time
        sim_start_time: simulation start time
        tiltdeg_colname: column name in data indicating tilt (degrees)
        time_colname: column name in data indicating time (seconds)

    Methods
        create_trajectory: create KML model and linestring objects tracing
            missile trajectory
        set_sim_start_end_times: calculate and set simulation start/end times
    """
    
    def __init__(
        self,
        data: Optional[pd.DataFrame] = None,
        collada_model_link: Optional[str] = None,
        collada_model_scale: Optional[float] = None,
        launch_time: datetime = datetime.now(),
        time_colname: str = 'time_sec',
        latdeg_colname: str = 'lat_deg',
        londeg_colname: str = 'lon_deg',
        altkm_colname: str = 'alt_km',
        bearingdeg_colname: str = 'bearing_deg',
        tiltdeg_colname: str = 'tilt_deg',
        kml_time_format: str = '%Y-%m-%dT%H:%M:%SZ',
    ) -> None:
        """Instantiate KMLTrajectorySim class.
        
        Arguments
            data: pandas DataFrame containing trajectory data
            collada_model_link: path or URL to 3D model in COLLADA format (.dae)
            collada_model_scale: scale factor for all 3D model axes (x, y, and z)
            launch_time: date and time of missile launch
            time_colname: column name in data indicating time (seconds)
            latdeg_colname: column name in data indicating latitude (degrees)
            londeg_colname: column name in data indicating longitude (degrees)
            altkm_colname: column name in data indicating altitude (kilometers)
            bearingdeg_colname: column name in data indicating bearing (degrees)
            tiltdeg_colname: column name in data indicating tilt (degrees)
            kml_time_format: string format for KML timestamps/timespans
        """
        self.data = data.sort_values([time_colname]).reset_index(drop=True)
        self.model_link = collada_model_link
        self.model_scale = collada_model_scale
        self.launch_time = launch_time
        self.time_colname = time_colname
        self.latdeg_colname = latdeg_colname
        self.londeg_colname = londeg_colname
        self.altkm_colname = altkm_colname
        self.bearingdeg_colname = bearingdeg_colname
        self.tiltdeg_colname = tiltdeg_colname
        self.kml_time_format = kml_time_format
        self.kml = simplekml.Kml()
        self.set_sim_start_end_times()
        
    def set_sim_start_end_times(
        self,
        start_time_buffer_sec: float = 10,
        end_time_buffer_sec: float = 10,
    ) -> None:
        """Calculate and set simulation start/end times.
        
        Arguments
            start_time_buffer_sec: seconds before launch to start simulation
            end_time_buffer_sec: seconds after impact to end simulation
        """
        self.sim_start_time = (self.launch_time - timedelta(
            seconds=(self.data[self.time_colname].min() + start_time_buffer_sec)
        )).strftime(self.kml_time_format)
        self.sim_end_time = (self.launch_time + timedelta(
            seconds=(self.data[self.time_colname].max() + end_time_buffer_sec)
        )).strftime(self.kml_time_format)

    def create_trajectory(self) -> None:
        """Create KML model and linestring objects tracing missile trajectory."""
        linestring_style = kml_utils.create_kml_linestring_style(
            color=simplekml.Color.blanchedalmond,
            width=2,
        )
        for idx in self.data.index:
            position_dict = self.data.loc[idx].to_dict()
            kml_folder_name = (f'Position at t={position_dict[self.time_colname]}')
            kml_folder = self.kml.newfolder(name=kml_folder_name)
            # Determine start/end times for models and linestrings
            if idx == self.data.index.min():
                timespan_begin = self.sim_start_time
            else:
                timespan_begin = (self.launch_time + timedelta(
                    seconds=position_dict[self.time_colname]
                )).strftime(self.kml_time_format)
            if idx == self.data.index.max():
                timespan_end = self.sim_end_time
            else:
                next_position_dict = self.data.loc[idx+1].to_dict()
                timespan_end = (self.launch_time + timedelta(
                    seconds=next_position_dict[self.time_colname]
                )).strftime(self.kml_time_format)
            # Add 3D model
            kml_utils.add_kml_model(
                kml_folder=kml_folder,
                lat_deg=position_dict[self.latdeg_colname],
                lon_deg=position_dict[self.londeg_colname],
                alt_meters=geo.km_to_meters(position_dict[self.altkm_colname]),
                collada_model_link=self.model_link,
                heading_deg=position_dict[self.bearingdeg_colname],
                tilt_deg=position_dict[self.tiltdeg_colname],
                roll_deg=0,
                x_scale=self.model_scale,
                y_scale=self.model_scale,
                z_scale=self.model_scale,
                timespan_begin=timespan_begin,
                timespan_end=timespan_end,
            )
            # Add linestring indicating trajectory over previous timestep
            if idx != self.data.index.min():
                prev_position_dict = self.data.loc[idx-1].to_dict()       
                kml_utils.add_kml_linestring(
                    kml_folder=kml_folder,
                    lon_lat_alt_list=[
                        (prev_position_dict[self.londeg_colname],
                         prev_position_dict[self.latdeg_colname],
                         geo.km_to_meters(prev_position_dict[self.altkm_colname])
                         ),
                        (position_dict[self.londeg_colname],
                         position_dict[self.latdeg_colname],
                         geo.km_to_meters(position_dict[self.altkm_colname])
                         ),
                    ],
                    style=linestring_style,
                    timespan_begin=timespan_begin,
                    #TODO: add timespan end as 10 seconds after impact
                )
