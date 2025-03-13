"""
Intercptor missile classes.

Contents:
    Public classes:
        TerminalInterceptor (in progress)
"""
# Import packages
from collections import OrderedDict
from typing import Dict, Optional, Type

import numpy as np

import simplekml

from src.kml_converters import KMLTrajectoryConverter
from src.missiles_abstract import Missile
from src.missiles_ballistic import BallisticMissile
from src.utils import get_constants
from src.utils_geo import (
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
        self.build_data = None
        self.trajectory_data = None

    def set_intercept_target(self, targeted_missile: BallisticMissile) -> None:
        """Identify missile to intercept."""
        self.targeted_missile = targeted_missile

    def get_intercept_position(self) -> None:
        """Identify latitude, longitude, and altitude of intercept location."""
        if self.targeted_missile is None:
            raise ValueError("Attribute 'targeted_missile' must be set (currently None).")
        intercept_dist_from_missile_LP_km = (
            self.targeted_missile.build_data["launchpoint_dist_to_target_km"] 
            - self.params["intercept_distance_from_target_km"]
        )
        intercept_time_sec = (
            intercept_dist_from_missile_LP_km 
            / self.targeted_missile.build_data["horizontal_velocity_km_sec"]
        )
        self.intercept_position = (
            self.targeted_missile.get_current_position(intercept_time_sec)
        )

    def build(self) -> None:
        """Compute static characteristics of interceptor:
            - Launchpoint ground distance to intercept (km)
            - Launchpoint distance to intercept (km)
            - Launchpoint bearing (deg)
            - Total time-to-intercept (seconds)
            - Horizontal velocity (km/s)
            - Initial vertical velocity (km/s)
            - Initial launch velocity (km/s)
            - Initial launch angle (degrees)
        """
        self.get_intercept_position()
        self.AP_latlon_deg = (
            self.intercept_position["lat_deg"], self.intercept_position["lon_deg"]
        )
        ground_dist_to_intercept_km = self.compute_distance_to_target(self.LP_latlon_deg)
        dist_to_intercept_km = (
            (ground_dist_to_intercept_km**2 + self.intercept_position["alt_km"]**2) ** (1/2)
        )
        
        self.build_data = {
            'launchpoint_ground_dist_to_intercept_km':ground_dist_to_intercept_km,
            'launchpoint_dist_to_intercept_km':dist_to_intercept_km,
            'launchpoint_bearing_deg':self.compute_bearing(self.LP_latlon_deg),
            'total_time_to_intercept_sec':None,
            'horizontal_velocity_km_sec':self.params['horizontal_velocity_km_sec'],
            'initial_vertical_velocity_km_sec':None,
            'initial_launch_velocity_km_sec':None,
            'initial_launch_angle_deg':None,
        }

    def launch(self, stoptime_sec: Optional[float] = None) -> None:
        """Record missile position (latitude, longitude, altitude) and orientation
        (heading, tilt, and roll) for each timestep from launch until impact.
        
        Arguments
            stoptime_sec: maximum time (seconds) for which to calculate missile
                position and orientation; if None (default), use total time to 
                target
        """
        pass

    def get_current_position(self, elapsed_time_sec: float) -> Dict:
        """Compute the current latitude/longitude (degrees) and altitude (km)
        of missile based on elapsed time since launch (seconds).

        Arguments
            elapsed_time_sec: elapsed time since launch (seconds)

        Returns
            dict containing lat_deg, lon_deg, and alt_km
        """
        pass

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
        pass

    # def set_intercept_surface_to_air_distance(self) -> None:
    #     """Compute and set the straight-line distance between interceptor launch
    #     point and intercept location."""
    #     interceptor_LP_vector = geo.convert_lat_lon_alt_to_nvector(
    #         lat_deg=self.LP_latlon_deg[0],
    #         lon_deg=self.LP_latlon_deg[1],
    #     )
    #     intercept_position_vector = geo.convert_lat_lon_alt_to_nvector(
    #         lat_deg=self.intercept_position_dict['lat_deg'],
    #         lon_deg=self.intercept_position_dict['lon_deg'],
    #         alt_km=self.intercept_position_dict['alt_km'],
    #     )
    #     self.intercept_surface_to_air_dist_km = geo.calculate_magnitude_dist_bt_vectors(
    #         interceptor_LP_vector, intercept_position_vector,
    #     )

    def missile_in_interceptor_ground_range(self) -> bool:
        """If max range set, determine if targeted missile trajectory 
        is within ground range of interceptor at any point prior to impact."""
        pass # calculate_cross_track_distance