"""
Repository: geospatial-visualizations
Application: Missile Intercepts (KML)
Sources:
    - University of Florida, Department of Mechanical & Aerospace Engineering
    (https://mae.ufl.edu/~uhk/ICBM.pdf)
    - MIT Department of Aeronautics and Astronautics
    (https://web.mit.edu/16.unified/www/FALL/systems/Lab_Notes/traj.pdf)
    - NASA Glenn Research Center
    (https://www.grc.nasa.gov/www/k-12/airplane/ballflght.html)
"""
# Import packages
from typing import Union
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
GRAV_CONSTANT = 6.673 * (10**-11)
GRAVITY_ACCEL_KM_PER_S2 = 0.0098
EARTH_RADIUS_KM = 6378
EARTH_ESCAPE_VELOCITY = np.sqrt(2 * GRAVITY_ACCEL_KM_PER_S2 * EARTH_RADIUS_KM)

# Define functions
def compute_angular_velocity(
    launch_velocity_km_per_sec: float,
    launch_angle_deg: float,
    altitude_km: float,
) -> float:
    """Calculate velocity in the angular direction given launch velocity in km/s,
    launch angle in degrees, and altitude above Earth's surface in km.
    """
    launch_angle_rad = geo.degrees_to_radians(launch_angle_deg)
    distance_km = launch_velocity_km_per_sec * np.cos(launch_angle_rad)
    ang_dist_rad = distance_km / (altitude_km + EARTH_RADIUS_KM)
    ang_di(EARTH_RADIUS_KM * launch_velocity_km_per_sec * np.cos(geo.degrees_to_radians(launch_angle_deg))) 
    / (altitude_km + EARTH_RADIUS_KM)
    

def compute_max_altitude(
    launch_velocity_km_per_sec: float,
    launch_angle_deg: float
) -> Union[None, float]:
    """Calculate maximum altitude of ballistic trajectory given initial launch velocity
    in km/s and launch angle in degrees. Source: https://mae.ufl.edu/~uhk/ICBM.pdf.
    """
    alpha = 2 * GRAVITY_ACCEL_KM_PER_S2 * EARTH_RADIUS_KM / launch_velocity_km_per_sec**2
    beta = geo.degrees_to_radians(launch_angle_deg)
    b2_minus_4ac = (alpha**2) - (4 * (1 - alpha) * (-1 * np.cos(beta)**2))
    y_solution = -1 + (((-1 * alpha) - np.sqrt(b2_minus_4ac)) / (2 * (1 - alpha)))
    max_alt_km = y_solution * EARTH_RADIUS_KM
    return max_alt_km

def compute_time_until_max_altitude(
    
) -> float:
    """Calculate time in seconds until projectile reaches maximum altitude.
    Source: https://mae.ufl.edu/~uhk/ICBM.pdf.
    """






compute_max_altitude(
    launch_velocity_km_per_sec=EARTH_ESCAPE_VELOCITY,
    launch_angle_deg=90,
)

compute_max_altitude(
    launch_velocity_km_per_sec=5.593,
    launch_angle_deg=30,
)

compute_max_altitude(
    launch_velocity_km_per_sec=EARTH_ESCAPE_VELOCITY,
    launch_angle_deg=0,
)

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