"""BallisticMissile and InterceptorMissile classes."""

# Import packages
from typing import Optional
import inspect
import os
import sys

import numpy as np

# Import local modules
scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(scriptdir)
sys.path.insert(0, parentdir)
import geo_utils as geo
import kml_utils

# Define constants
EARTH_RADIUS_KM = 6378
EARTH_MASS_KG = 5.9722 * (10**24)

GRAVITY_ACCEL_KM_PER_S2 = 0.0098
GRAV_CONSTANT_M3_PER_KG_S2 = 6.673 * (10**-11)
EARTH_STD_GRAV_PARAM_M3_PER_S2 = GRAV_CONSTANT_M3_PER_KG_S2 * EARTH_MASS_KG

EARTH_ESCAPE_VELOCITY_KM_PER_S = (
    np.sqrt(2 * EARTH_STD_GRAV_PARAM_M3_PER_S2 / (EARTH_RADIUS_KM*1000)) / 1000
)

# Define classes
class BallisticMissile():
    """Base class for missiles with ballistic trajectories."""
    
    def __init__(
        self,
        launch_lat_deg: Optional[float] = None,
        launch_lon_deg: Optional[float] = None,
        aimpoint_lat_deg: Optional[float] = None,
        aimpoint_lon_deg: Optional[float] = None,
        time_to_target_sec: Optional[float] = None,
#        launch_angle_deg: Optional[float] = None,
#        launch_velo_km_per_sec: Optional[float] = None,
    ) -> None:
        """Instantiate BallisticMissile class.
        
        Arguments
            launch_lat_deg: Launchpoint latitude in degrees
            launch_lon_deg: Launchpoint longitude in degrees
            aimpoint_lat_deg: Aimpoint latitude in degrees
            aimpoint_lon_deg: Aimpoint longitude in degrees
            time_to_target_sec: Total time (in seconds) for missile to travel
                from launchpoint to aimpoint
            launch_angle_deg: Initial launch angle in degrees
            launch_velo_km_per_sec: Initial launch velocity in km/second
        """
        self.launch_latlon_deg = [launch_lat_deg, launch_lon_deg]
        self.aimpoint_latlon_deg = [aimpoint_lat_deg, aimpoint_lon_deg]
        self.time_to_target_sec = time_to_target_sec
#        self.launch_angle_rad = geo.deg_to_rad(launch_angle_deg)
#        self.launch_velo_km_per_sec = launch_velo_km_per_sec

    def build(self) -> None:
        """Set all initial launch parameters for missile."""
        if not self.launch_latlon_deg or None in self.launch_latlon_deg:
            launch_lat_deg = float(input('Enter launch latitude: '))
            launch_lon_deg = float(input('Enter launch longitude: '))
            self.set_launchpoint(launch_lat_deg, launch_lon_deg)
        if not self.aimpoint_latlon_deg or None in self.aimpoint_latlon_deg:
            aimpoint_lat_deg = float(input('Enter aimpoint latitude: '))
            aimpoint_lon_deg = float(input('Enter aimpoint longitude: '))
            self.set_aimpoint(aimpoint_lat_deg, aimpoint_lon_deg)
        if self.time_to_target_sec is None:
            time_to_target_sec = float(input('Enter time to target (sec): '))
            self.set_time_to_target(time_to_target_sec)
        self.set_distance_to_target()
        self.set_horizontal_velocity()
        self.set_max_change_in_vertical_velocity()
        self.set_initial_vertical_velocity()
        self.set_initial_launch_velocity()
        self.set_initial_launch_angle()

    def launch(): #TODO
        pass
    
    def set_launchpoint(
        self,
        launch_lat_deg: float,
        launch_lon_deg: float,
    ) -> None:
        """Set launchpoint latitude and longitude after instantiation.
        
        Arguments
            launch_lat_deg: Launchpoint latitude in degrees
            launch_lon_deg: Launchpoint longitude in degrees
        """
        self.launch_latlon_deg = [launch_lat_deg, launch_lon_deg]

    def set_aimpoint(
        self,
        aimpoint_lat_deg: float,
        aimpoint_lon_deg: float,
    ) -> None:
        """Set aimpoint latitude and longitude after instantiation.
        
        Arguments
            aimpoint_lat_deg: Aimpoint latitude in degrees
            aimpoint_lon_deg: Aimpoint longitude in degrees
        """
        self.aimpoint_latlon_deg = [aimpoint_lat_deg, aimpoint_lon_deg]

    def set_time_to_target(
        self,
        time_to_target_sec: float,
    ) -> None:
        """Set time to target (in seconds) after instantiation.
        
        Arguments
            time_to_target_sec: Total time (in seconds) for missile to travel
                from launchpoint to aimpoint
        """
        self.time_to_target_sec = time_to_target_sec

    def set_distance_to_target(self) -> float:
        """Compute and set great-circle distance (in km) between 
        launchpoint and aimpoint."""
        if not self.launch_latlon_deg or None in self.launch_latlon_deg:
            print('Launchpoint coordinates not set. Distance could not be calculated.')
        elif not self.aimpoint_latlon_deg or None in self.aimpoint_latlon_deg:
            print('Aimpoint coordinates not set. Distance could not be calculated.')
        else:
            self.dist_to_target_km = geo.calculate_great_circle_distance(
                origin_lat_deg=self.launch_latlon_deg[0],
                origin_lon_deg=self.launch_latlon_deg[1],
                dest_lat_deg=self.aimpoint_latlon_deg[0],
                dest_lon_deg=self.aimpoint_latlon_deg[1],
            )

    def set_horizontal_velocity(self) -> None:
        """Compute and set horizontal velocity (km/sec).
        Note that horizontal velocity is constant over entire trajectory."""
        if self.time_to_target_sec is None:
            print('Time to target not provided. Horizontal velocity could '+ 
                  'not be calculated.')
        else:
            if self.dist_to_target_km is None:
                self.set_distance_to_target()
            self.horiz_vel_km_per_sec = (
                self.dist_to_target_km / self.time_to_target_sec
            )

    def set_max_change_in_vertical_velocity(self) -> None:
        """Compute and set the maximum change in vertical velocity 
        if ballistic missile reachs target."""
        if self.time_to_target_sec is None:
            print('Time to target not set. Maximum change in vertical '+
                  'velocity could not be calculated.')
        else:
            self.max_change_vert_vel_km_per_sec = (
                self.time_to_target_sec * GRAVITY_ACCEL_KM_PER_S2
            )
    
    def set_initial_vertical_velocity(self) -> None:
        """Compute and set initial vertical velocity (km/sec).
        Change in vertical velocity w.r.t. time is the gravitational
        acceleration at Earth's surface (approx. 0.0098 km/s^2)."""
        if self.max_change_vert_vel_km_per_sec is None:
            self.set_max_change_in_vertical_velocity()
        self.initial_vert_vel_km_per_sec = (
            0.5 * self.max_change_vert_vel_km_per_sec # Vertical velocity = 0 at midpoint
        )
    
    def set_initial_launch_velocity(self) -> None:
        """Compute and set initial launch velocity (km/sec)."""
        if self.horiz_vel_km_per_sec is None:
            self.set_horizontal_velocity()
        if self.initial_vert_vel_km_per_sec is None:
            self.set_initial_vertical_velocity()
        self.initial_launch_vel_km_per_sec = np.sqrt(
            self.horiz_vel_km_per_sec**2 + self.initial_vert_vel_km_per_sec**2
        )
        print('Initial launch velocity calculated to be '+
              f'{round(self.initial_launch_vel_km_per_sec, 2)} km/s.')
        if self.initial_launch_vel_km_per_sec >= EARTH_ESCAPE_VELOCITY_KM_PER_S:
            print('Initial launch velocity exceeds Earth escape velocity. '+
                  'Recommend increasing total time to target.')
            #TODO in later versions: automatically adjust launch velocity
        
    def set_initial_launch_angle(self) -> None:
        """Compute and set initial launch angle (degrees)."""
        if self.horiz_vel_km_per_sec is None:
            self.set_horizontal_velocity()
        if self.initial_vert_vel_km_per_sec is None:
            self.set_initial_vertical_velocity()
        self.initial_launch_angle_deg = geo.rad_to_deg(
            np.arctan(
                self.initial_vert_vel_km_per_sec / self.horiz_vel_km_per_sec
            )
        )
        print('Initial launch angle is '+
              f'{round(self.initial_launch_angle_deg, 2)} degrees.')

    def update_current_position_and_velocity(): #TODO
        pass
    
    def compute_vertical_velocity(
        launch_angle_deg: float,
        initial_vel_km_per_sec: Optional[float] = None,
        horiz_vel_km_per_sec: Optional[float] = None,
    ) -> float:
        """Compute vertical velocity (km/s) given horizontal or initial velocity.
        
        Arguments
            launch_angle_deg: Initial launch angle in degrees
            initial_vel_km_per_sec: Initial launch velocity in km/second
            horiz_vel_km_per_sec: Horizontal velocity in km/second
        
        Returns
            Vertical velocity in km/second
        """
        launch_angle_rad = geo.deg_to_rad(launch_angle_deg)
        if initial_vel_km_per_sec is not None:
            return initial_vel_km_per_sec * np.sin(launch_angle_rad)
        elif horiz_vel_km_per_sec is not None:
            return horiz_vel_km_per_sec * np.tan(launch_angle_rad)
        else:
            print('Initial or horizontal velocity must be provided to '+
                  'calculate vertical velocity.')


if __name__ == '__main__':
    test_missile = BallisticMissile()
    test_missile.set_launchpoint(39.7392, 104.9903)
    test_missile.set_aimpoint(41.1400, 104.8202)
    test_missile.set_time_to_target(150)
    test_missile.build()        
    test_missile.__dict__

# =============================================================================
# Archive
# =============================================================================
#def compute_max_altitude(
#    launch_velocity_km_per_sec: float,
#    launch_angle_deg: float
#) -> Union[None, float]:
#    """Calculate maximum altitude of ballistic trajectory given initial launch velocity
#    in km/s and launch angle in degrees. Source: https://mae.ufl.edu/~uhk/ICBM.pdf.
#    """
#    alpha = 2 * GRAVITY_ACCEL_KM_PER_S2 * EARTH_RADIUS_KM / launch_velocity_km_per_sec**2
#    beta = geo.degrees_to_radians(launch_angle_deg)
#    b2_minus_4ac = (alpha**2) - (4 * (1 - alpha) * (-1 * np.cos(beta)**2))
#    y_solution = -1 + (((-1 * alpha) - np.sqrt(b2_minus_4ac)) / (2 * (1 - alpha)))
#    max_alt_km = y_solution * EARTH_RADIUS_KM
#    return max_alt_km
#
#compute_max_altitude(
#    launch_velocity_km_per_sec=EARTH_ESCAPE_VELOCITY,
#    launch_angle_deg=90,
#)
#
#compute_max_altitude(
#    launch_velocity_km_per_sec=5.593,
#    launch_angle_deg=30,
#)
#
#compute_max_altitude(
#    launch_velocity_km_per_sec=EARTH_ESCAPE_VELOCITY,
#    launch_angle_deg=0,
#)