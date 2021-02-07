"""Utility functions for geodetic calculations."""

# Import packages
from typing import List, Tuple
import numpy as np

# Define constants
EARTH_RADIUS_KM = 6378

# Define functions
def km_to_miles(km: float) -> float:
    """Converts distance in kilometers to miles."""
    return km * 0.62137

def km_to_meters(km: float) -> float:
    """Converts distance in kilometers to meters."""
    return km * 1000

def meters_to_km(meters: float) -> float:
    """Converts distance in meters to kilometers."""
    return meters / 1000

def deg_to_rad(degrees: float) -> float:
    """Converts angle in degrees to radians."""
    return degrees * np.pi / 180

def rad_to_deg(radians: float) -> float:
    """Converts angle in radians to degrees."""
    return radians * 180 / np.pi

def convert_trig_to_compass_angle(trig_angle: float, radians: bool = True):
    """Converts a trigonometric angle (measured counterclockwise from East) 
    to compass angle (measured clockwise from North). Angle returned is in 
    original units (e.g., radians are returned if polar_angle is given in radians).
    
    Arguments
        trig_angle: angle measured counterclockwise from East
        radians: indicates that angle is given in radians (False=degrees)
        
    Returns
        compass_angle: angle measured clockwise from North
    """
    if radians:
        compass_angle = ((np.pi / 2) - trig_angle) % (2 * np.pi)
    else:
        compass_angle = (90 - trig_angle) % 360
    return compass_angle

def calculate_great_circle_distance(
    origin_lat_deg: float, origin_lon_deg: float,
    dest_lat_deg: float, dest_lon_deg: float,
) -> float:
    """Calculate great-circle distance in kilometers between two points using the
    haversine formula. Source: https://www.movable-type.co.uk/scripts/latlong.html.

    Arguments
        origin_lat_deg: float latitude of origin location in decimal degrees
        origin_lon_deg: float longitude of origin location in decimal degrees
        dest_lat_deg: float latitude of destination location in decimal degrees
        dest_lon_deg: float longitude of destination location in decimal degrees

    Returns
        distance_km: float distance in kilometers between location #1 and #2
    """
    # Convert degrees to radians
    origin_lat_rad = deg_to_rad(origin_lat_deg)
    origin_lon_rad = deg_to_rad(origin_lon_deg)
    dest_lat_rad = deg_to_rad(dest_lat_deg)
    dest_lon_rad = deg_to_rad(dest_lon_deg)
    # Calculate distance
    delta_lat_rad = dest_lat_rad - origin_lat_rad
    delta_lon_rad = dest_lon_rad - origin_lon_rad
    a = (
        np.sin(delta_lat_rad/2) ** 2
        + np.cos(origin_lat_rad) * np.cos(dest_lat_rad) * np.sin(delta_lon_rad/2) ** 2
    )
    ang_dist_rad = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    distance_km = EARTH_RADIUS_KM * ang_dist_rad
    return distance_km

def calculate_initial_bearing(
    origin_lat_deg: float, origin_lon_deg: float,
    dest_lat_deg: float, dest_lon_deg: float,
) -> float:
    """Calculate forward azimuth/initial bearing between two points, in degrees.
    Source: https://www.movable-type.co.uk/scripts/latlong.html.    
    
    Arguments
        origin_lat_deg: float latitude of origin location in decimal degrees
        origin_lon_deg: float longitude of origin location in decimal degrees
        dest_lat_deg: float latitude of destination location in decimal degrees
        dest_lon_deg: float longitude of destination location in decimal degrees

    Returns
        bearing_deg: float initial bearing in degrees
    """
    # Convert degrees to radians
    origin_lat_rad = deg_to_rad(origin_lat_deg)
    origin_lon_rad = deg_to_rad(origin_lon_deg)
    dest_lat_rad = deg_to_rad(dest_lat_deg)
    dest_lon_rad = deg_to_rad(dest_lon_deg)
    # Calculate bearing
    delta_lon_rad = dest_lon_rad - origin_lon_rad
    x = (np.cos(origin_lat_rad) * np.sin(dest_lat_rad) 
        - np.sin(origin_lat_rad) * np.cos(dest_lat_rad) * np.cos(delta_lon_rad)
    )
    y = np.sin(delta_lon_rad) * np.cos(dest_lat_rad)
    theta = np.arctan2(y, x)
    bearing_deg = (rad_to_deg(theta) + 360) % 360
    return bearing_deg

def determine_destination_coords(
    origin_lat_deg: float, origin_lon_deg: float,
    distance_km: float, initial_bearing_deg: float
) -> List[float]:
    """Determine the latitude and longitude of a destination point given an
    initial latitude, longitude, and bearing (clockwise from 0 degrees North).
    Source: https://www.movable-type.co.uk/scripts/latlong.html.
    
    Arguments
        origin_lat_deg: float latitude of origin location in decimal degrees
        origin_lon_deg: float longitude of origin location in decimal degrees
        distance_km: float distance in km from origin to destination
        initial_bearing_deg: float bearing in degrees from origin to destination
    
    Returns
        [dest_lat_deg, dest_lon_deg]: list containing two float values for
        latitude and longitude of destination in decimal degrees
        """
    # Convert degrees to radians
    origin_lat_rad = deg_to_rad(origin_lat_deg)
    origin_lon_rad = deg_to_rad(origin_lon_deg)
    bearing_rad = deg_to_rad(initial_bearing_deg)
    # Determine latitude/longitude of destination
    ang_dist_rad = distance_km / EARTH_RADIUS_KM
    dest_lat_rad = np.arcsin(np.sin(origin_lat_rad) * np.cos(ang_dist_rad)
        + np.cos(origin_lat_rad) * np.sin(ang_dist_rad) * np.cos(bearing_rad)
    )
    dest_lon_rad = (origin_lon_rad 
        + np.arctan2(
            np.sin(bearing_rad) * np.sin(ang_dist_rad) * np.cos(origin_lat_rad),
            np.cos(ang_dist_rad) - np.sin(origin_lat_rad) * np.sin(dest_lat_rad)
        )
    )
    # Convert radians to degrees
    dest_lat_deg = rad_to_deg(dest_lat_rad)
    dest_lon_deg = rad_to_deg(dest_lon_rad)
    return [dest_lat_deg, dest_lon_deg]

def determine_square_coords(
    origin_lat_deg: float,
    origin_lon_deg: float,
    side_length_meters: float,
    rotation_radians: float = 0,
) -> List[Tuple[float, float]]:
    """Determine the latitude and longitude of four points that form a square
    centered around the origin point.
    
    Arguments
        origin_lat_deg: float latitude of center point in decimal degrees
        origin_lon_deg: float longitude of center point in decimal degrees
        side_length_meters: float length of square in meters
        rotation_radians: float radians indicating rotation of square around origin

    Returns
        coords_list: list containing four tuples of latitude-longitude pairs
                     indicating the corners of the square around the origin
    """
    coords_list = []
    dist_origin_to_corner_meters = np.sqrt(2 * (side_length_meters/2)**2)
    angle_rad_list = [(((n*2+1)/4)*np.pi + rotation_radians) for n in np.arange(4)]
    for angle_rad in angle_rad_list:
        bearing_rad = convert_trig_to_compass_angle(angle_rad, radians=True)
        latlon_list = determine_destination_coords(
            origin_lat_deg=origin_lat_deg,
            origin_lon_deg=origin_lon_deg,
            distance_km=meters_to_km(dist_origin_to_corner_meters),
            initial_bearing_deg=rad_to_deg(bearing_rad),
        )
        coords_list.append((latlon_list[1], latlon_list[0])) # Longitude first for simplekml
    return coords_list
