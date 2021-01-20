"""
Repository: missile-intercepts
Description: Define classes for ballistic and interceptor missiles
Sources:
    - University of Florida, Department of Mechanical & Aerospace Engineering
    (https://mae.ufl.edu/~uhk/ICBM.pdf)
    - MIT Department of Aeronautics and Astronautics
    (https://web.mit.edu/16.unified/www/FALL/systems/Lab_Notes/traj.pdf)
    - NASA Glenn Research Center
    (https://www.grc.nasa.gov/www/k-12/airplane/ballflght.html)
"""
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
GRAV_CONSTANT_M3_PER_KG_S2 = 6.673 * (10**-11)
EARTH_MASS_KG = 5.9722 * (10**24)
EARTH_STD_GRAV_PARAM_M3_PER_S2 = GRAV_CONSTANT_M3_PER_KG_S2 * EARTH_MASS_KG
EARTH_RADIUS_KM = 6378
EARTH_ESCAPE_VELOCITY_KM_PER_S = (
    np.sqrt(2 * EARTH_STD_GRAV_PARAM_M3_PER_S2 / (EARTH_RADIUS_KM*1000)) / 1000
)
GRAVITY_ACCEL_KM_PER_S2 = 0.0098

# Define classes
class BallisticMissile():
    """ """
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

    def set_distance(self) -> float:
        """Set great-circle distance (in km) between launchpoint and aimpoint."""
        if not self.launch_latlon_deg or not self.aimpoint_latlon_deg:
            print('Launchpoint or aimpoint coordinates not set. Distance '+
                  'could not be calculated.')
        else:
            self.dist_km = geo.calculate_great_circle_distance(
                origin_lat_deg=self.launch_latlon_deg[0],
                origin_lon_deg=self.launch_latlon_deg[1],
                dest_lat_deg=self.aimpoint_latlon_deg[0],
                dest_lon_deg=self.aimpoint_latlon_deg[1],
            )

    def set_horizontal_velocity(self) -> None:
        """Compute and set horizontal velocity (km/sec) attribute.
        Note that horizontal velocity is constant over entire trajectory.
        """
        if self.time_to_target_sec is None:
            print('Time to target not provided. Horizontal velocity could '+ 
                  'not be calculated.')
            return
        if self.dist_km is None:
            self.set_distance()
        self.horiz_vel_km_per_sec = self.dist_km / self.time_to_target_sec

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
            vert_vel_km_per_sec: Vertical velocity in km/second
        """
        launch_angle_rad = geo.deg_to_rad(launch_angle_deg)
        if initial_vel_km_per_sec is not None:
            return initial_vel_km_per_sec * np.sin(launch_angle_rad)
        elif horiz_vel_km_per_sec is not None:
            return horiz_vel_km_per_sec * np.tan(launch_angle_rad)
        else:
            print('Initial or horizontal velocity must be provided to '+
                  'calculate vertical velocity.')

        
        
        

        
        



# =============================================================================
# Archive
# =============================================================================
#def compute_horizontal_velocity(velocity: float, theta_rad: float) -> float:
#    """Calculate horizontal component of velocity."""
#    return velocity * np.cos(theta_rad)
#
#def compute_vertical_velocity(velocity: float, theta_rad: float) -> float:
#    """Calculate verticle component of velocity."""
#    return velocity * np.sin(theta_rad)
#
#def compute_distance(initial_horizontal_velocity: float, time: float) -> float:
#    """Calculate distance traveled (x-direction) for given time."""
#    return initial_horizontal_velocity * time
#
#def compute_altitude(initial_vertical_velocity: float, time: float) -> float:
#    """Calculate altitude (y-direction) for given time."""
#    return (initial_vertical_velocity * time) - (0.5 * GRAVITY_ACCEL_KM_PER_S2 * time**2)
#
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