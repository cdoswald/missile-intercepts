"""BallisticMissile and InterceptorMissile classes."""

# Import packages
from abc import ABC
from collections import OrderedDict
import inspect
import os
import sys
from typing import Optional

import numpy as np
import pandas as pd

# Import local modules
script_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.join(script_dir, 'Utils'))
import geo_utils as geo

# Define constants
EARTH_RADIUS_KM = 6378
EARTH_MASS_KG = 5.9722 * (10**24)
GRAVITY_ACCEL_KM_PER_S2 = (-0.0098)
GRAV_CONSTANT_M3_PER_KG_S2 = 6.673 * (10**-11)
EARTH_STD_GRAV_PARAM_M3_PER_S2 = GRAV_CONSTANT_M3_PER_KG_S2 * EARTH_MASS_KG
EARTH_ESCAPE_VELOCITY_KM_PER_S = (
    np.sqrt(2 * EARTH_STD_GRAV_PARAM_M3_PER_S2 / (EARTH_RADIUS_KM*1000)) / 1000
)

# Define classes
class BallisticMissile():
    """Base class for missiles with ballistic trajectories.
    
    Attributes
        aimpoint_latlon_deg: aimpoint latitude and longitude (decimal degrees)
        current_altitude_km: current timestep altitude (kilometers)
        current_bearing_deg: current timestep bearing (degrees)
        current_latlon_deg: current timestep latitude and longitude (decimal degrees)
        current_tilt_deg: current timestep tilt (degrees)
        dist_to_target_km: distance between launchpoint and aimpoint (kilometers)
        horiz_vel_km_per_sec: horizontal velocity (constant, kilometers per second)
        initial_launch_angle_deg: initial launch angle (degrees)
        initial_launch_vel_km_per_sec: initial velocity at launch, in the direction
            of initial launch angle (kilometers per second)
        initial_vert_vel_km_per_sec: initial vertical velocity at launch
            (kilometers per second)
        launch_latlon_deg: launchpoint latitude and longitude (decimal degrees)
        launchpoint_initial_bearing_deg: forward azimuth/initial bearing from
            launchpoint to aimpoint (degrees, clockwise from North)
        max_change_vert_vel_km_per_sec: maximum change in vertical velocity
            (kilometers per second)
        time_to_target_sec: total time (in seconds) for missile to travel
            from launchpoint to aimpoint
        trajectory_data: pandas DataFrame containing latitude, longitude, 
            altitude, bearing, and tilt for each timestep index
        
    Methods
        build: set all initial launch parameters
        compute_current_bearing: compute forward azimuth/initial bearing from 
            current position to aimpoint
        compute_current_vertical_velocity: compute vertical velocity given
            elapsed time
        launch: record missile position for each timestep from launch until impact
        set_aimpoint: set aimpoint latitude/longitude after instantiation
        set_distance_to_target: compute and set distance between launchpoint
            and aimpoint
        set_horizontal_velocity: compute and set (constant) horiztonal velocity
        set_initial_launch_angle: compute and set initial launch angle
        set_initial_launch_velocity: compute and set initial velocity at launch
            in the direction of launch angle
        set_initial_vertical_velocity: compute and set initial vertical velocity
            at launch
        set_launchpoint: set launchpoint latitude/longitude after instantiation
        set_launchpoint_bearing: compute and set forward azimuth/initial bearing
            from launchpoint to aimpoint
        set_max_change_in_vertical_velocity: compute and set maximum change
            in vertical velocity (if missile reaches target)
        set_time_to_target: set time to target after instantiation
        update_current_position: update latitude, longitude, altitude, bearing,
            and tilt given elapsed time
    """

    def __init__(
        self,
        launch_lat_deg: Optional[float] = None,
        launch_lon_deg: Optional[float] = None,
        aimpoint_lat_deg: Optional[float] = None,
        aimpoint_lon_deg: Optional[float] = None,
        time_to_target_sec: Optional[float] = None,
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
        self.set_launchpoint_bearing()
        self.set_horizontal_velocity()
        self.set_max_change_in_vertical_velocity()
        self.set_initial_vertical_velocity()
        self.set_initial_launch_velocity()
        self.set_initial_launch_angle()

    def launch(self, timestep_sec: float = 1) -> None:
        """Record missile position (latitude, longitude, altitude, bearing)
        for each timestep from launch until impact.
        
        Arguments
            timestep_sec: Timestep interval in seconds
        """
        trajectory_dict = OrderedDict()
        for elapsed_time_sec in np.arange(
            start=0,
            stop=self.time_to_target_sec + timestep_sec,
            step=timestep_sec,
        ):
            self.update_current_position(elapsed_time_sec)
            trajectory_dict[elapsed_time_sec] = {
                'lat_deg':self.current_latlon_deg[0],
                'lon_deg':self.current_latlon_deg[1],
                'alt_km':self.current_altitude_km,
                'bearing_deg':self.current_bearing_deg,
                'tilt_deg':self.current_tilt_deg,
            }
        self.trajectory_data = (
            pd.DataFrame.from_dict(trajectory_dict, orient='index')
            .reset_index()
            .rename(columns={'index':'time_sec'})
        )

    def update_current_position(
        self,
        elapsed_time_sec: float,
    ) -> None:
        """Update latitude, longitude, altitude, bearing (heading), and tilt
        based on elapsed time.

        Arguments
            elapsed_time_sec: Elapsed time since launch (in seconds)
        """
        # Latitude/longitude
        dist_traveled_km = self.horiz_vel_km_per_sec * elapsed_time_sec
        self.current_latlon_deg = geo.determine_destination_coords(
            origin_lat_deg=self.launch_latlon_deg[0],
            origin_lon_deg=self.launch_latlon_deg[1],
            distance_km=dist_traveled_km,
            initial_bearing_deg=self.launchpoint_initial_bearing_deg,
        )
        # Altitude (integrate current vertical velocity formula)
        self.current_altitude_km = (
            self.initial_vert_vel_km_per_sec * elapsed_time_sec
            + (0.5 * GRAVITY_ACCEL_KM_PER_S2 * elapsed_time_sec**2)
        )
        # Bearing/heading (from current position)
        self.current_bearing_deg = self.compute_current_bearing(
            position_lat_deg=self.current_latlon_deg[0],
            position_lon_deg=self.current_latlon_deg[1],
        )
        # Tilt (from current position)
        self.current_tilt_deg = geo.rad_to_deg(
            geo.convert_trig_to_compass_angle(
                np.arctan2(
                    self.compute_current_vertical_velocity(elapsed_time_sec),
                    self.horiz_vel_km_per_sec
                )
            )
        )

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

    def set_distance_to_target(self) -> None:
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

    def set_launchpoint_bearing(self) -> None:
        """Compute and set forward azimuth/initial bearing from launchpoint
        to aimpoint. Bearing measured in degrees, clockwise from North."""
        if not self.launch_latlon_deg or None in self.launch_latlon_deg:
            print('Launchpoint coordinates not set. Bearing could not be calculated.')
        elif not self.aimpoint_latlon_deg or None in self.aimpoint_latlon_deg:
            print('Aimpoint coordinates not set. Bearing could not be calculated.')
        else:
            self.launchpoint_initial_bearing_deg = geo.calculate_initial_bearing(
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
                self.time_to_target_sec * abs(GRAVITY_ACCEL_KM_PER_S2)
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
            
    def compute_current_bearing(
        self,
        position_lat_deg: float,
        position_lon_deg: float,
    ) -> float:
        """Compute forward azimuth/initial bearing from current location to 
        aimpoint. Bearing measured in degrees, clockwise from North."""
        current_bearing_deg = geo.calculate_initial_bearing(
            origin_lat_deg=position_lat_deg,
            origin_lon_deg=position_lon_deg,
            dest_lat_deg=self.aimpoint_latlon_deg[0],
            dest_lon_deg=self.aimpoint_latlon_deg[1],
            )
        return current_bearing_deg
        
    def compute_current_vertical_velocity(self, elapsed_time_sec: float) -> float:
        """Compute vertical velocity (km/s) given elapsed time in seconds.
        
        Arguments
            elapsed_time_sec: Elapsed time since launch (in seconds)
        
        Returns
            current_vert_vel_km_per_sec: Current vertical velocity (km/s)
        """
        if elapsed_time_sec > self.time_to_target_sec:
            print(f'Elapsed time of {elapsed_time_sec} seconds exceeds total '+
                  'time to target. Vertical velocity not calculated.')
        else:
            if self.initial_vert_vel_km_per_sec is None:
                self.set_initial_vertical_velocity()
            current_vert_vel_km_per_sec = (
                self.initial_vert_vel_km_per_sec 
                + GRAVITY_ACCEL_KM_PER_S2 * elapsed_time_sec
            )
            return current_vert_vel_km_per_sec
