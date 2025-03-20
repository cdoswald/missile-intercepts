"""
Interceptor missile classes.

Contents:
    Public classes:
        TerminalInterceptor [IN PROGRESS]
"""
# Import packages
from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Dict, Optional, Type

import numpy as np

import simplekml

from src.kml_converters import KMLTrajectoryConverter
from src.missiles_abstract import Missile
from src.missiles_ballistic import BallisticMissile
from src.utils import get_constants
from src.utils_geo import (
    rad_to_deg,
    determine_destination_coords,
    convert_trig_to_compass_angle,
    calculate_cross_track_distance,
)

# Get constants
constants = get_constants()

# Define classes
class TerminalInterceptor(Missile):
    """Base class for terminal phase interceptors.

    Attributes

    Methods

    """
    
    def __init__(self, params: Dict) -> None:
        """Instantiate TerminalInterceptor.
        
        Arguments:

        """
        super().__init__(params)
        self.targeted_missile = None
        self.intercept_position = None
        self.intercept_time_sec = None

    def set_intercept_target(self, targeted_missile: BallisticMissile) -> None:
        """Identify missile to intercept."""
        self.targeted_missile = targeted_missile

    def get_intercept_time_and_position(self) -> None:
        """Calculate time (seconds) and position (latitude, longitude, altitude)
        after enemy missile launch until intercept."""
        if self.targeted_missile is None:
            raise ValueError("Attribute 'targeted_missile' must be set (currently None).")
        intercept_dist_from_missile_LP_km = (
            self.targeted_missile.build_data["launchpoint_dist_to_target_km"] 
            - self.params["intercept_distance_from_target_km"]
        )
        self.intercept_time_sec = (
            intercept_dist_from_missile_LP_km 
            / self.targeted_missile.build_data["horizontal_velocity_km_sec"]
        )
        self.intercept_position = (
            self.targeted_missile.get_current_position(self.intercept_time_sec)
        )

    def build(self) -> None:
        """Compute static characteristics of interceptor:
            - Launchpoint ground distance to intercept (km)
            - Launchpoint distance to intercept (km)
            - Launchpoint bearing (deg)
            - Interceptor time-to-intercept (seconds)
            - Horizontal velocity (km/s)
            - Initial vertical velocity (km/s)
            - Initial launch velocity (km/s)
            - Initial launch angle (degrees)
        """
        self.get_intercept_time_and_position()
        self.AP_latlon_deg = (
            self.intercept_position["lat_deg"], self.intercept_position["lon_deg"]
        )
        ground_dist_to_intercept_km = self.compute_distance_to_target(self.LP_latlon_deg)
        dist_to_intercept_km = (
            (ground_dist_to_intercept_km**2 + self.intercept_position["alt_km"]**2) ** (1/2)
        )
        interceptor_time_to_intercept_sec = (
            ground_dist_to_intercept_km / self.params["horizontal_velocity_km_sec"]
        )
        initial_vertical_velocity_km_sec = self.compute_initial_vertical_velocity(
            interceptor_time_to_intercept_sec
        )
        initial_launch_velocity_km_sec = self.compute_velocity(
            self.params['horizontal_velocity_km_sec'],
            initial_vertical_velocity_km_sec,
        )
        initial_launch_angle_deg = self.compute_altitude_angle(
            self.params['horizontal_velocity_km_sec'],
            initial_vertical_velocity_km_sec,
        )
        self.build_data = {
            'launchpoint_ground_dist_to_intercept_km':ground_dist_to_intercept_km,
            'launchpoint_dist_to_intercept_km':dist_to_intercept_km,
            'launchpoint_bearing_deg':self.compute_bearing(self.LP_latlon_deg),
            'interceptor_time_to_intercept_sec':interceptor_time_to_intercept_sec,
            'horizontal_velocity_km_sec':self.params['horizontal_velocity_km_sec'],
            'initial_vertical_velocity_km_sec':initial_vertical_velocity_km_sec,
            'initial_launch_velocity_km_sec':initial_launch_velocity_km_sec,
            'initial_launch_angle_deg':initial_launch_angle_deg,
        }
        self.params["launch_time"] = self.get_interceptor_launch_time()

    def launch(self, stoptime_sec: Optional[float] = None) -> None:
        """Record interceptor position (latitude, longitude, altitude) and orientation
        (heading, tilt, and roll) for each timestep from launch until impact.
        
        Arguments
            stoptime_sec: maximum time (seconds) for which to calculate missile
                position and orientation; if None (default), use interceptor time to intercept
        """
        traj_dict = OrderedDict()
        if stoptime_sec is None:
            stoptime_sec = self.build_data['interceptor_time_to_intercept_sec']
        for elapsed_time_sec in np.arange(0, stoptime_sec, self.params['timestep_sec']):
            position_dict = self.get_current_position(elapsed_time_sec)
            orientation_dict = self.get_current_orientation(elapsed_time_sec)
            traj_dict[elapsed_time_sec] = {**position_dict, **orientation_dict}
        # Final position and orientation
        traj_dict[round(stoptime_sec, 3)] = {
            **self.get_current_position(stoptime_sec),
            **self.get_current_orientation(stoptime_sec)
        }
        self.trajectory_data = traj_dict

    def get_current_position(self, elapsed_time_sec: float) -> Dict:
        """Compute the current latitude/longitude (degrees) and altitude (km)
        of missile based on elapsed time since launch (seconds).

        Arguments
            elapsed_time_sec: elapsed time since launch (seconds)

        Returns
            dict containing lat_deg, lon_deg, and alt_km
        """
        dist_km = self.build_data['horizontal_velocity_km_sec'] * elapsed_time_sec
        current_latlon_deg = determine_destination_coords(
            origin_lat_deg=self.LP_latlon_deg[0],
            origin_lon_deg=self.LP_latlon_deg[1],
            distance_km=dist_km,
            initial_bearing_deg=self.build_data['launchpoint_bearing_deg'],
        )
        # Integrate vertical velocity formula
        current_altitude_km = ( 
            self.build_data['initial_vertical_velocity_km_sec'] * elapsed_time_sec
            + (0.5 * constants['GRAVITY_ACCEL_KM_PER_S2'] * elapsed_time_sec**2)
        )
        return {
            'lat_deg':current_latlon_deg[0],
            'lon_deg':current_latlon_deg[1],
            'alt_km':max(current_altitude_km, 0),
        }

    def get_current_orientation(self, elapsed_time_sec: float) -> Dict:
        """Compute the heading, tilt, and roll (degrees) for current position
        based on elapsed time since launch (seconds).
        Note: For version 0.1.0, COLLADA missile representations are
        assumed to be symmetrical, and roll is always set to 0 degrees.

        Arguments
            elapsed_time_sec: elapsed time since launch (seconds)

        Returns
            dict containing bearing_deg, tilt_deg, and roll_deg
        """
        position_dict = self.get_current_position(elapsed_time_sec)
        position_latlon_deg = (position_dict['lat_deg'], position_dict['lon_deg'])
        current_bearing_deg = self.compute_bearing(position_latlon_deg)
        current_tilt_deg = rad_to_deg(convert_trig_to_compass_angle(np.arctan2(
            self.compute_current_vertical_velocity(elapsed_time_sec),
            self.build_data['horizontal_velocity_km_sec'],
        )))
        return {
            'bearing_deg':current_bearing_deg,
            'tilt_deg':current_tilt_deg,
            'roll_deg':0,
        }

    def get_interceptor_launch_time(self):
        """Calculate interceptor launch time in absolute terms relative to
        enemy missile launch time."""
        interceptor_launch_time = (
            self.targeted_missile.params["launch_time"] 
            + timedelta(seconds=self.intercept_time_sec)
            - timedelta(seconds=self.build_data["interceptor_time_to_intercept_sec"])
        )
        return interceptor_launch_time

    def compute_initial_vertical_velocity(self, time_to_intercept_sec: float) -> float:
        """Compute initial vertical velocity (km/s) at time of launch to reach
        final intercept altitude (km). Solves for initial velocity in integrated
        altitude formula.

        Arguments:
            time_to_intercept_sec: interceptor time-to-intercept (seconds)

        Returns:
            initial vertical velocity (km/s)
        """
        gravity_drop = (0.5 * constants['GRAVITY_ACCEL_KM_PER_S2'] * time_to_intercept_sec**2)
        return (self.intercept_position["alt_km"] - gravity_drop) / time_to_intercept_sec

    def compute_current_vertical_velocity(self, elapsed_time_sec: float) -> float:
        """Compute vertical velocity (km/s) given time since launch (seconds).
        
        Arguments:
            elapsed_time_sec: Elapsed time since launch (in seconds)

        Returns:
            current vertical velocity (km/s)
        """
        change_in_velocity = constants['GRAVITY_ACCEL_KM_PER_S2'] * elapsed_time_sec
        return (self.build_data['initial_vertical_velocity_km_sec'] + change_in_velocity)

    def check_missile_in_interceptor_ground_range(self) -> bool:
        """If max range set, determine if targeted missile trajectory 
        is within ground range of interceptor at any point prior to impact."""
        pass # calculate_cross_track_distance