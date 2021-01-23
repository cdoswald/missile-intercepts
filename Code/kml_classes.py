"""KMLTrajectory and KMLCamera classes."""

#TODO: Define styles (possibly in utils)
#TODO: Add stylemap (in utils)
#TODO: Add point for final timestep
#TODO: Check hemisphere coordinates
#TODO: Add save KMZ functions to utils
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
scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(scriptdir)
sys.path.insert(0, parentdir)
import kml_utils

# Define constants
EARTH_RADIUS_KM = 6378

# Define classes
class KMLTrajectorySim():
    """Base class for simulating a missile trajectory in KML."""
    
    def __init__(
        self,
        data: Optional[pd.DataFrame] = None,
        launch_time: datetime = datetime.now(),
        time_colname: str = 'time_sec',
        latdeg_colname: str = 'lat_deg',
        londeg_colname: str = 'lon_deg',
        altm_colname: str = 'alt_m',
        kml_time_format: str = '%Y-%m-%dT%H:%M:%SZ',
    ) -> None:
        """Instantiate KMLTrajectorySim class.
        
        Arguments
            data: pandas DataFrame containing trajectory data
            launch_time: date and time of missile launch
            time_colname: name of time column in data
            latdeg_colname: name of latitude (degrees) column in data
            londeg_colname: name of longitude (degrees) column in data
            altm_colname: name of altitude (meters) column in data
            kml_time_format: string format for KML timestamps/timespans
        """
        self.data = data.sort_values([time_colname]).reset_index(drop=True)
        self.launch_time = launch_time
        self.time_colname = time_colname
        self.latdeg_colname = latdeg_colname
        self.londeg_colname = londeg_colname
        self.altm_colname = altm_colname
        self.kml_time_format = kml_time_format
        self.kml = simplekml.Kml()

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
        """Create KML points and linestrings tracing missile trajectory."""
        self.set_sim_start_end_times()
        for idx in self.data.index:
            kml_folder = self.kml.newfolder(name=f'Point {idx}')
            position_dict = self.data.loc[idx].to_dict()
            # Determine start/end times for points and linestrings
            if idx == self.data.index.min():
                timespan_begin = self.sim_start_time
            else:
                timespan_begin = (self.launch_time + timedelta(
                    seconds=position_dict[self.time_colname]
                )).strftime(self.kml_time_format)
            if idx == self.data.index.max():
                pnt_timespan_end = self.sim_end_time
            else:
                next_position_dict = self.data.loc[idx+1].to_dict()
                pnt_timespan_end = (self.launch_time + timedelta(
                    seconds=next_position_dict[self.time_colname]
                )).strftime(self.kml_time_format)
            # Add point indicating current location of missile
            kml_utils.create_kml_point(
                kml_folder=kml_folder,
                lat_deg=position_dict[self.latdeg_colname],
                lon_deg=position_dict[self.londeg_colname],
                alt_meters=position_dict[self.altm_colname],
                style=simplekml.Style(), #TODO
#                    pnt_label=f'Time: {position_dict[self.time_col_name]}',
                timespan_begin=timespan_begin,
                timespan_end=pnt_timespan_end,
            )
            # Add linestring indicating trajectory over previous timestep
            if idx != self.data.index.min():
                prev_position_dict = self.data.loc[idx-1].to_dict()       
                kml_utils.create_kml_linestring(
                    kml_folder=kml_folder,
                    lon_lat_alt_list=[
                        (prev_position_dict[self.londeg_colname],
                         prev_position_dict[self.latdeg_colname],
                         prev_position_dict[self.altm_colname]
                         ),
                        (position_dict[self.londeg_colname],
                         position_dict[self.latdeg_colname],
                         position_dict[self.altm_colname]
                         ),
                    ],
                    style=simplekml.Style(), #TODO
                    label='',
                    timespan_begin=timespan_begin,
                    timespan_end='',
                    close_linestring=False,
                )


if __name__ == '__main__':
    kml_test = KMLTrajectorySim(data=data)
    kml_test.create_trajectory()
    kml_test.kml.savekmz('test.kml')
