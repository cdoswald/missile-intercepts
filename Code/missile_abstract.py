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

import geo_utils as geo

# Define classes
class Missile(ABC):
    """Template for all missile classes.

    Attributes:
        params: dict of user-defined parameter values
        LP_latlon_deg: tuple of launchpoint (latitude, longitude) in degrees
        AP_latlon_deg: tuple of aimpoint (latitutde, longitude) in degrees

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

    def __init__(
        self,
        params: Optional[Dict] = None,
        LP_latlon_deg: Optional[Tuple[float, float]] = None,
        AP_latlon_deg: Optional[Tuple[float, float]] = None,
    ) -> None:
        """Instantiate Missile class."""
        self.params = params
        self.LP_latlon_deg = LP_latlon_deg
        self.AP_latlon_deg = AP_latlon_deg

    @abstractmethod
    def build(self) -> None:
        """Set all initial launch parameters for missile."""

    @abstractmethod
    def launch(self, timestep_sec: float = 1) -> None:
        """Record missile position (latitude, longitude, and altitude) and
        orientation (heading, tilt, and roll) for each timestep from launch
        until impact.

        Arguments:
            timestep_sec: length of time step in seconds
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
        return geo.calculate_great_circle_distance(
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
            bearing (degrees)
        """
        return geo.calculate_initial_bearing(
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
        return geo.rad_to_deg(np.arctan(
            vertical_velocity_km_sec / horizontal_velocity_km_sec
        ))
        return current_bearing_deg