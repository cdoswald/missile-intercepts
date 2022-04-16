"""
Abstract missile base class.

Contents:
    Public classes:
        Missile (abstract)
"""
# Import packages
from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple

# Define classes
class Missile(ABC):
    """Template for all missile classes.

    Attributes:
        params: dict of user-defined parameter values
        LP_latlon_deg: tuple of launchpoint (latitude, longitude) in degrees
        AP_latlon_deg: tuple of aimpoint (latitutde, longitude) in degrees
        position: tuple of missile latitude, longitude, and altitude for timestep
        orientation: tuple of missile heading, tilt, and roll for timestep

    Methods:
        build (abstract)
        launch (abstract)
        get_current_position (abstract)
        get_current_orientation (abstract)
        set_launchpoint
        set_aimpoint
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
        self.position = None
        self.orientation = None

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
