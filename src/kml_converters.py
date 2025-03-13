"""
Keyhole Markup Language (KML) converter classes.

Contents:
    Public Classes:
        KMLTrajectoryConverter
"""
#TODO: Add stylemap (in utils_kml)
#TODO: Add camera classes to track missile trajectory

# Import packages
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

import simplekml

from src.utils import get_constants
from src.utils_geo import km_to_meters
from src.utils_kml import (
    add_kml_linestring,
    add_kml_model,
    create_kml_linestring_style,
)

# Get constants
constants = get_constants()

# Define classes
class KMLTrajectoryConverter():
    """Converts missile trajectory data to KML.
    
    Attributes
        params: dict of user-defined parameter values
        trajectory_data: dict of missile position/orientation for each timestep

    Methods
        create_kml_trajectory
        compute_timespan_start_end_times
        compute_sim_start_end_times
    """

    def __init__(
        self,
        params: Dict,
        trajectory_data: Optional[Dict] = None,
    ) -> None:
        """Instantiate KMLTrajectoryConverter class.
        
        Arguments
            params: dict of user-defined parameter values
            trajectory_data: dict of missile position/orientation for each timestep
        """
        self.params = params
        self.trajectory_data = trajectory_data

    def create_kml_trajectory(
        self,
        kml_document: simplekml.Document,
    ) -> simplekml.Document:
        """Create KML model and linestring objects for missile trajectory.
        
        Arguments:
            kml: simplekml document in which to add KML trajectory data

        Returns:
            simplekml document > missile folder > timestep folders > 
            COLLADA model and linestring elements
        """
        linestring_style = create_kml_linestring_style(
            color=simplekml.Color.blanchedalmond,
            width=2,
        )
        kml_missile_folder = kml_document.newfolder(name=self.params['missile_name'])
        for time_idx, position_dict in self.trajectory_data.items():
            kml_timestep_folder = kml_missile_folder.newfolder(
                name=f'position at t={time_idx}'
            )
            timespan_begin, timespan_end = self.compute_timespan_start_end_times(
                time_idx
            )
            # Add 3D model
            add_kml_model(
                kml_folder=kml_timestep_folder,
                lat_deg=position_dict['lat_deg'],
                lon_deg=position_dict['lon_deg'],
                alt_meters=km_to_meters(position_dict['alt_km']),
                collada_model_link=self.params['collada_model_path'],
                heading_deg=position_dict['bearing_deg'],
                tilt_deg=position_dict['tilt_deg'],
                roll_deg=position_dict['roll_deg'],
                x_scale=self.params['collada_model_scale'],
                y_scale=self.params['collada_model_scale'],
                z_scale=self.params['collada_model_scale'],
                timespan_begin=timespan_begin.strftime(constants['KML_TIME_FORMAT']),
                timespan_end=timespan_end.strftime(constants['KML_TIME_FORMAT']),
            )
            # Add linestring indicating trajectory over previous timestep
            if time_idx != min(self.trajectory_data.keys()):
                prev_time_idx = time_idx - self.params['timestep_sec']
                prev_position_dict = self.trajectory_data[prev_time_idx]  
                lon_lat_alt_list = [
                    (
                        prev_position_dict['lon_deg'],
                        prev_position_dict['lat_deg'],
                        km_to_meters(prev_position_dict['alt_km'])
                     ),
                    (  
                        position_dict['lon_deg'],
                        position_dict['lat_deg'],
                        km_to_meters(position_dict['alt_km'])
                    ),
                ]
                add_kml_linestring(
                    kml_folder=kml_timestep_folder,
                    lon_lat_alt_list=lon_lat_alt_list,
                    style=linestring_style,
                    timespan_begin=timespan_begin.strftime(constants['KML_TIME_FORMAT']),
                    timespan_end='',
                )
        return kml_document

    def compute_timespan_start_end_times(
        self,
        time_idx: float,
    ) -> Tuple[datetime, datetime]:
        """Calculate model and linestring start/end times.
        
        Arguments:
            time_idx: float time index for trajectory data

        Returns:
            tuple of datetime (timespan_start, timespan_end)
        """
        sim_start_time, sim_end_time = self.compute_sim_start_end_times()
        if time_idx == min(self.trajectory_data.keys()):
            timespan_start = sim_start_time
        else:
            timespan_start = self.params['launch_time'] + timedelta(
                seconds=time_idx
            )
        if time_idx == max(self.trajectory_data.keys()):
            timespan_end = sim_end_time
        else:
            timespan_end = self.params['launch_time'] + timedelta(
                seconds=(time_idx + self.params['timestep_sec'])
            )
        return timespan_start, timespan_end

    def compute_sim_start_end_times(self) -> Tuple[datetime, datetime]:
        """Calculate simulation start/end times.
        
        Returns:
            tuple of datetime (sim_start_time, sim_end_time)
        """
        sim_start_time = self.params['launch_time'] - timedelta(
            seconds=self.params['sim_start_time_buffer_sec']
        )
        sim_end_time = self.params['launch_time'] + timedelta(
            seconds=(
                max(self.trajectory_data.keys()) 
                + self.params['sim_end_time_buffer_sec']
            )
        )
        return sim_start_time, sim_end_time
