"""
Abstract missile base class.

Contents:
    Public classes:
        Missile (abstract)
"""
# Import packages
from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple

import numpy as np

import simplekml

from src.kml_converters import KMLTrajectoryConverter
from src.utils_geo import (
    calculate_great_circle_distance,
    calculate_initial_bearing,
    rad_to_deg,
)

# Define classes
class Missile(ABC):
    """Template for all missile classes.

    Attributes:
        params: dict of user-defined parameter values
        LP_latlon_deg: tuple of launchpoint (latitude, longitude) in degrees
        AP_latlon_deg: tuple of aimpoint (latitude, longitude) in degrees

    Methods:
        build (abstract)
        launch (abstract)
        get_current_position (abstract)
        get_current_orientation (abstract)
        set_launchpoint
        set_aimpoint
        compute_distance_to_target
        compute_bearing
        compute_velocity
        compute_altitude_angle
    """

    def __init__(self, params: Optional[Dict] = None) -> None:
        """Instantiate Missile class.

        Arguments
            params: dict of user-defined parameter values
        """
        self.params = params
        self.LP_latlon_deg = params.get('LP_latlon_deg', None)
        self.AP_latlon_deg = params.get('AP_latlon_deg', None)
        self.build_data = None
        self.trajectory_data = None

    @abstractmethod
    def build(self) -> None:
        """Set all initial launch parameters for missile."""

    @abstractmethod
    def launch(self) -> None:
        """Record missile position (latitude, longitude, and altitude) and
        orientation (heading, tilt, and roll) for each timestep from launch
        until impact.
        """

    @abstractmethod
    def get_current_position(self, elapsed_time_sec: float) -> None:
        """Get the latitude, longitude, and altitude of current position
        based on elapsed time.

        Arguments:
            elapsed_time_sec: elapsed time since launch in seconds
        """

    @abstractmethod
    def get_current_orientation(self, elapsed_time_sec: float) -> None:
        """Get the heading, tilt, and roll for current position based on
        elapsed time.

        Arguments:
            elapsed_time_sec: elapsed time since launch in seconds
        """

    def set_launchpoint(self, LP_latlon_deg: Tuple[float, float]) -> None:
        """Set launchpoint latitude and longitude in decimal degrees.

        Arguments
            LP_latlon_deg: tuple of launchpoint (latitude, longitude) in degrees
        """
        self.LP_latlon_deg = LP_latlon_deg

    def set_aimpoint(self, AP_latlon_deg: Tuple[float, float]) -> None:
        """Set aimpoint latitude and longitude in decimal degrees.

        Arguments
            AP_latlon_deg: tuple of aimpoint (latitude, longitude) in degrees
        """
        self.AP_latlon_deg = AP_latlon_deg

    def compute_distance_to_target(
        self,
        position_latlon_deg: Tuple[float, float],
    ) -> float:
        """Compute great-circle distance (km) between current position and target.
        
        Arguments:
            position_latlon_deg: tuple of missile's latitude, longitude (degrees)
        
        Returns:
            distance to target (km)
        """
        return calculate_great_circle_distance(
            position_latlon_deg[0], position_latlon_deg[1],
            self.AP_latlon_deg[0], self.AP_latlon_deg[1],
        )

    def compute_bearing(
        self,
        position_latlon_deg: Tuple[float, float],
    ) -> float:
        """Compute forward azimuth/initial bearing (degrees, clockwise from
        North) from current position to aimpoint.
    
        Arguments:
            position_latlon_deg: tuple of missile's latitude, longitude (degrees)

        Returns
            bearing from position to aimpoint (degrees, clockwise from North)
        """
        return calculate_initial_bearing(
            position_latlon_deg[0], position_latlon_deg[1],
            self.AP_latlon_deg[0], self.AP_latlon_deg[1],
        )

    def compute_velocity(
        self,
        horizontal_velocity_km_sec: float,
        vertical_velocity_km_sec: float,
    ) -> float:
        """Compute velocity (km/s) based on horizontal and vertical 
        components of velocity (km/s).

        Arguments:
            horizontal_velocity_km_sec: horizontal velocity (km/s)
            vertical_velocity_km_sec: vertical velocity (km/s)

        Returns:
            forward velocity (km/s)
        """
        return np.sqrt(
            horizontal_velocity_km_sec**2 + vertical_velocity_km_sec**2
        )

    def compute_altitude_angle(
        self,
        horizontal_velocity_km_sec: float,
        vertical_velocity_km_sec: float,
    ) -> float:
        """Compute altitude angle (degrees) based on horizontal and vertical
        components of velocity (km/s).

        Arguments:
            horizontal_velocity_km_sec: horizontal velocity (km/s)
            vertical_velocity_km_sec: vertical velocity (km/s)

        Returns:
            altitude angle (degrees)
        """
        return rad_to_deg(np.arctan(
            vertical_velocity_km_sec / horizontal_velocity_km_sec
        ))
    
    def create_kml_trajectory(
        self,
        kml_document: simplekml.Document,
        folder_name: str,
        traj_color: simplekml.Color,
        traj_width: int = 2,
    ) -> simplekml.Document:
        """Convert missile trajectory data to KML.

        Arguments:
            kml_document: simplekml document in which to add KML trajectory data

        Returns:
            simplekml document > missile folder > timestep folders > 
            COLLADA model and linestring elements
        """
        kml_converter = KMLTrajectoryConverter(
            self.params,
            self.trajectory_data,
        )
        return kml_converter.create_kml_trajectory(
            kml_document,
            folder_name,
            traj_color,
            traj_width,
        )