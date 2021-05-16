"""Missile (abstract), BallisticMissile, and InterceptorMissile classes."""

# Import packages
from abc import ABC, abstractmethod
from collections import OrderedDict
import inspect
import os
import sys
from typing import Dict, Optional, Type

import numpy as np
import pandas as pd

# Import local modules
from kml_classes import KMLTrajectorySim
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
class Missile(ABC):
    """Template for all missile classes."""
    
    def __init__(
        self,
        LP_lat_deg: Optional[float] = None,
        LP_lon_deg: Optional[float] = None,
    ) -> None:
        """Instantiate missile with launchpoint latitude and longitude.
        
        Arguments
            LP_lat_deg: Launchpoint latitude in degrees
            LP_lon_deg: Launchpoint longitude in degrees
        """
        self.LP_latlon_deg = (LP_lat_deg, LP_lon_deg)
    
    @abstractmethod
    def build(self) -> None:
        """Set all initial launch parameters for missile."""
    
    @abstractmethod
    def launch(self, timestep_sec: float = 1) -> None:
        """Record missile position (latitude, longitude, altitude, bearing, tilt)
        for each timestep from launch until impact."""

    @abstractmethod
    def get_current_position(self, elapsed_time_sec: float) -> None:
        """Get the latitude, longitue, and altitude of current position 
        based on elapsed time."""

    @abstractmethod
    def get_current_orientation(self, elapsed_time_sec: float) -> None:
        """Get the heading, tilt, and roll for current position based on 
        elapsed time."""
    
    @abstractmethod
    def set_horizontal_velocity(self) -> None:
        """Compute and set horizontal velocity (km/sec)."""

    @abstractmethod
    def set_initial_launch_velocity(self) -> None:
        """Compute and set initial launch velocity (km/sec)."""

    @abstractmethod
    def set_initial_launch_angle(self) -> None:
        """Compute and set initial launch angle (degrees)."""

    @abstractmethod
    def set_aimpoint(self) -> None:
        """Set aimpoint latitude and longitude."""

    def set_launchpoint(
        self,
        LP_lat_deg: float,
        LP_lon_deg: float,
    ) -> None:
        """Set launchpoint latitude and longitude after instantiation.
        
        Arguments
            LP_lat_deg: Launchpoint latitude in degrees
            LP_lon_deg: Launchpoint longitude in degrees
        """
        self.LP_latlon_deg = [LP_lat_deg, LP_lon_deg]

    def set_distance_to_target(self) -> None:
        """Compute and set great-circle distance (in km) between launchpoint 
        and aimpoint."""
        if not self.LP_latlon_deg or None in self.LP_latlon_deg:
            print('Launchpoint coordinates not set. Distance could not be calculated.')
        elif not self.AP_latlon_deg or None in self.AP_latlon_deg:
            print('Aimpoint coordinates not set. Distance could not be calculated.')
        else:
            self.dist_to_target_km = geo.calculate_great_circle_distance(
                origin_lat_deg=self.LP_latlon_deg[0],
                origin_lon_deg=self.LP_latlon_deg[1],
                dest_lat_deg=self.AP_latlon_deg[0],
                dest_lon_deg=self.AP_latlon_deg[1],
            )

    def set_launchpoint_bearing(self) -> None:
        """Compute and set forward azimuth/initial bearing from launchpoint
        to aimpoint. Bearing measured in degrees, clockwise from North."""
        if not self.LP_latlon_deg or None in self.LP_latlon_deg:
            print('Launchpoint coordinates not set. Bearing could not be calculated.')
        elif not self.AP_latlon_deg or None in self.AP_latlon_deg:
            print('Aimpoint coordinates not set. Bearing could not be calculated.')
        else:
            self.launchpoint_initial_bearing_deg = geo.calculate_initial_bearing(
                origin_lat_deg=self.LP_latlon_deg[0],
                origin_lon_deg=self.LP_latlon_deg[1],
                dest_lat_deg=self.AP_latlon_deg[0],
                dest_lon_deg=self.AP_latlon_deg[1],
            )

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
            dest_lat_deg=self.AP_latlon_deg[0],
            dest_lon_deg=self.AP_latlon_deg[1],
            )
        return current_bearing_deg


class BallisticMissile(Missile):
    """Base class for missiles with ballistic trajectories.
    
    Attributes
        AP_latlon_deg: aimpoint latitude and longitude (decimal degrees)
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
        kml_trajectory: missile trajectory in KML format
        LP_latlon_deg: launchpoint latitude and longitude (decimal degrees)
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
        create_kml_trajectory: create model trajectory in KML format
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
        LP_lat_deg: Optional[float] = None,
        LP_lon_deg: Optional[float] = None,
        AP_lat_deg: Optional[float] = None,
        AP_lon_deg: Optional[float] = None,
        time_to_target_sec: Optional[float] = None,
        intercept_ground_dist_from_TMAP_km: Optional[float] = None,
        collada_model_link: str = "../COLLADA/test_collada.dae",
        collada_model_scale: float = 200,
    ) -> None:
        """Instantiate BallisticMissile class.
        
        Arguments
            LP_lat_deg: Launchpoint latitude in degrees
            LP_lon_deg: Launchpoint longitude in degrees
            AP_lat_deg: Aimpoint latitude in degrees
            AP_lon_deg: Aimpoint longitude in degrees
            time_to_target_sec: Total time (in seconds) for missile to travel
                from launchpoint to aimpoint
            collada_model_link: path or URL to 3D model in COLLADA format (.dae)
            collada_model_scale: scale factor for all 3D model axes (x, y, and z)
        """
        super(BallisticMissile, self).__init__(LP_lat_deg, LP_lon_deg)
        self.AP_latlon_deg = (AP_lat_deg, AP_lon_deg)
        self.time_to_target_sec = time_to_target_sec
        self.intercept_ground_dist_from_TMAP_km = intercept_ground_dist_from_TMAP_km
        self.collada_model_link = collada_model_link
        self.collada_model_scale = collada_model_scale
        self.intercept_seconds_after_launch = None
            
    def build(self) -> None:
        """Set all initial launch parameters for missile."""
        if not self.LP_latlon_deg or None in self.LP_latlon_deg:
            LP_lat_deg = float(input('Enter launch latitude: '))
            LP_lon_deg = float(input('Enter launch longitude: '))
            self.set_launchpoint(LP_lat_deg, LP_lon_deg)
        if not self.AP_latlon_deg or None in self.AP_latlon_deg:
            AP_lat_deg = float(input('Enter aimpoint latitude: '))
            AP_lon_deg = float(input('Enter aimpoint longitude: '))
            self.set_aimpoint(AP_lat_deg, AP_lon_deg)
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
        self.set_intercept_time()

    def launch(self, timestep_sec: float = 1) -> None:
        """Record missile position (latitude, longitude, altitude) and orientation
        (heading, tilt, and roll) for each timestep from launch until impact.
        
        Arguments
            timestep_sec: Timestep interval in seconds
        """
        traj_dict = OrderedDict()
        if self.intercept_seconds_after_launch is not None:
            stop_time = self.intercept_seconds_after_launch
        else:
            stop_time = self.time_to_target_sec
        for elapsed_time_sec in np.arange(
            start=0,
            stop=stop_time + timestep_sec,
            step=timestep_sec,
        ):
            position_dict = self.get_current_position(elapsed_time_sec)
            orientation_dict = self.get_current_orientation(elapsed_time_sec)
            traj_dict[elapsed_time_sec] = {**position_dict, **orientation_dict}
        self.trajectory_data = (
            pd.DataFrame.from_dict(traj_dict, orient='index')
            .reset_index()
            .rename(columns={'index':'time_sec'})
        )

    def get_current_position(self, elapsed_time_sec: float) -> Dict[str, float]:
        """Get the latitude, longitue, and altitude of current position 
        based on elapsed time.

        Arguments
            elapsed_time_sec: elapsed time since launch (seconds)
        """
        current_latlon_deg = geo.determine_destination_coords(
            origin_lat_deg=self.LP_latlon_deg[0],
            origin_lon_deg=self.LP_latlon_deg[1],
            distance_km=(self.horiz_vel_km_per_sec * elapsed_time_sec),
            initial_bearing_deg=self.launchpoint_initial_bearing_deg,
        )
        # Integrate vertical velocity formula
        current_altitude_km = ( 
            self.initial_vert_vel_km_per_sec * elapsed_time_sec
            + (0.5 * GRAVITY_ACCEL_KM_PER_S2 * elapsed_time_sec**2)
        ) 
        current_position_dict = {
            'lat_deg':current_latlon_deg[0],
            'lon_deg':current_latlon_deg[1],
            'alt_km':current_altitude_km,
        }
        return current_position_dict

    def get_current_orientation(self, elapsed_time_sec: float) -> Dict[str, float]:
        """Get the heading, tilt, and roll for current position based on 
        elapsed time.

        Arguments
            elapsed_time_sec: elapsed time since launch (seconds)
        """
        current_position_dict = self.get_current_position(elapsed_time_sec)
        current_bearing_deg = self.compute_current_bearing(
            position_lat_deg=current_position_dict['lat_deg'],
            position_lon_deg=current_position_dict['lon_deg'],
        )
        current_tilt_deg = geo.rad_to_deg(
            geo.convert_trig_to_compass_angle(
                np.arctan2(
                    self.compute_current_vertical_velocity(elapsed_time_sec),
                    self.horiz_vel_km_per_sec
                )
            )
        )
        current_orientation_dict = {
            'bearing_deg':current_bearing_deg,
            'tilt_deg':current_tilt_deg,
            'roll_deg':0,
        }
        return current_orientation_dict

    def set_aimpoint(
        self,
        AP_lat_deg: float,
        AP_lon_deg: float,
    ) -> None:
        """Set aimpoint latitude and longitude after instantiation.
        
        Arguments
            AP_lat_deg: Aimpoint latitude in degrees
            AP_lon_deg: Aimpoint longitude in degrees
        """
        self.AP_latlon_deg = (AP_lat_deg, AP_lon_deg)

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

    def set_intercept_time(self) -> None:
        """Compute and set the time of intercept in seconds after launch, 
        given intercept distance from targeted missile aimpoint (TMAP)."""
        if self.intercept_ground_dist_from_TMAP_km is not None:
            self.intercept_seconds_after_launch = (
                (self.dist_to_target_km - self.intercept_ground_dist_from_TMAP_km)
                / self.horiz_vel_km_per_sec
            )
        else:
            self.intercept_seconds_after_launch = None

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

    def create_kml_trajectory(self) -> None:
        """Create missile trajectory in KML format."""
        kml_trajectory_sim = KMLTrajectorySim(
            data=self.trajectory_data,
            collada_model_link=self.collada_model_link,
            collada_model_scale=self.collada_model_scale,
        )
        kml_trajectory_sim.create_trajectory()
        self.kml_trajectory = kml_trajectory_sim.kml


class TerminalPhaseInterceptor(Missile):
    """Base class for terminal phase interceptors.
    
    Attributes
        initial_launch_vel_km_per_sec: initial velocity at launch, in the 
            direction of initial launch angle (kilometers per second)
        intercept_dist_from_TMAP_km: intercept point distance from targeted 
            missile aimpoint (TMAP) (kilometers)
        LP_latlon_deg: interceptor launchpoint latitude and longitude 
            (decimal degrees)
        max_ground_range_km: maximum ground range of interceptor (kilometers)
        targeted_missile: BallisticMissile to intercept in terminal phase

    Methods
    
    """
    
    def __init__(
        self,
        IMLP_lat_deg: Optional[float] = None,
        IMLP_lon_deg: Optional[float] = None,
        targeted_missile: Optional[Type[BallisticMissile]] = None,
        max_ground_range_km: Optional[float] = None,
        intercept_ground_dist_from_TMAP_km: Optional[float] = None,
        initial_launch_vel_km_per_sec: Optional[float] = None,
        collada_model_link: str = "../COLLADA/test_collada.dae",
        collada_model_scale: float = 200,
    ) -> None:
        """Instantiate TerminalPhaseInterceptor class.
        
        Arguments
            LP_lat_deg: Launchpoint latitude in degrees
            LP_lon_deg: Launchpoint longitude in degrees
            targeted_missile: missile targeted for interception in terminal phase
            max_ground_range_km: maximum ground range of interceptor (kilometers)
            intercept_dist_from_TMAP_km: intercept point distance from 
                targeted missile aimpoint (TMAP) (kilometers)
            initial_launch_vel_km_per_sec: initial launch velocity of interceptor,
                in the direction of initial launch angle (kilometers per second)
        """
        super(TerminalPhaseInterceptor, self).__init__(IMLP_lat_deg, IMLP_lon_deg)
#        import pdb; pdb.set_trace()
        self.targeted_missile = targeted_missile
        self.max_ground_range_km = max_ground_range_km
        self.intercept_ground_dist_from_TMAP_km = intercept_ground_dist_from_TMAP_km
        self.initial_launch_vel_km_per_sec = initial_launch_vel_km_per_sec
        self.collada_model_link = collada_model_link
        self.collada_model_scale = collada_model_scale
        self.AP_latlon_deg = None
        self.intercept_ground_dist_from_IMLP_km = None
        self.intercept_seconds_after_TM_launch = None
        self.intercept_position_dict = None
        self.intercept_surface_to_air_dist_km = None
        self.intercept_launch_time_seconds = None
        self.intercept_flight_time_seconds = None
        self.horiz_vel_km_per_sec = None
        self.launchpoint_initial_bearing_deg = None
        self.initial_launch_angle_deg = None
        self.trajectory_data = None
        self.kml_trajectory = None

    def determine_missile_in_ground_range(self) -> bool:
        """If max range set, determine if targeted missile trajectory 
        is within ground range of interceptor at any point prior to impact."""
        min_ground_dist_to_TM_traj_km = geo.calculate_cross_track_distance(
            origin_lat_deg=self.targeted_missile.LP_latlon_deg[0],
            origin_lon_deg=self.targeted_missile.LP_latlon_deg[1],
            dest_lat_deg=self.targeted_missile.AP_latlon_deg[0],
            dest_lon_deg=self.targeted_missile.AP_latlon_deg[1],
            cross_lat_deg=self.LP_latlon_deg[0],
            cross_lon_deg=self.LP_latlon_deg[1],
            )
        if self.max_ground_range >= min_ground_dist_to_TM_traj_km:
            #TODO: create green KML polygon indicating within range
            return True
        else:
            #TODO: create red KML polygon indicating out of range
            return False

    def build(self) -> None:
        """Set all initial launch parameters for interceptor missile."""
        if not self.determine_missile_in_ground_range:
            print('Targeted missile trajectory is out of interceptor\'s '+
                  f'{self.max_ground_range_km} km ground range.')
        else:
            self.set_intercept_time()
            self.set_intercept_position()
            self.set_aimpoint()
            self.set_intercept_ground_dist_from_IMLP()
            self.set_intercept_surface_to_air_distance()
            self.set_intercept_flight_time()
            self.set_intercept_launch_time()
            self.set_horizontal_velocity()
            self.set_launchpoint_bearing()
            self.set_initial_launch_angle()
            
    def launch(self, timestep_sec: float = 1) -> None:
        """Record missile position (latitude, longitude, altitude) and orientation
        (heading, tilt, and roll) for each timestep from launch until impact.
        
        Arguments
            timestep_sec: Timestep interval in seconds
        """
        traj_dict = OrderedDict()
        for elapsed_time_sec in np.arange(
            start=0,
            stop=self.intercept_seconds_after_TM_launch + timestep_sec,
            step=timestep_sec,
        ):
            position_dict = self.get_current_position(elapsed_time_sec)
            orientation_dict = self.get_current_orientation(elapsed_time_sec)
            traj_dict[elapsed_time_sec] = {**position_dict, **orientation_dict}
        self.trajectory_data = (
            pd.DataFrame.from_dict(traj_dict, orient='index')
            .reset_index()
            .rename(columns={'index':'time_sec'})
        )

    def get_current_position(self, elapsed_time_sec: float) -> Dict[str, float]:
        """Get the latitude, longitude, and altitude of current position 
        based on elapsed time.

        Arguments
            elapsed_time_sec: elapsed time since targeted missile launch (seconds)
        """
        # Calculate elapsed time of interceptor flight
        interceptor_flight_elapsed_time_sec = max(
            elapsed_time_sec - self.intercept_launch_time_seconds, 0
        )
        # Calculate latitude/longitude
        current_latlon_deg = geo.determine_destination_coords(
            origin_lat_deg=self.LP_latlon_deg[0],
            origin_lon_deg=self.LP_latlon_deg[1],
            distance_km=(self.horiz_vel_km_per_sec * interceptor_flight_elapsed_time_sec),
            initial_bearing_deg=self.launchpoint_initial_bearing_deg,
        )
        # Calculate altitude
        current_altitude_km = (
            self.intercept_position_dict['alt_km'] / self.intercept_flight_time_seconds
            * interceptor_flight_elapsed_time_sec
        )
        current_position_dict = {
            'lat_deg':current_latlon_deg[0],
            'lon_deg':current_latlon_deg[1],
            'alt_km':current_altitude_km,
        }
        return current_position_dict

    def get_current_orientation(self, elapsed_time_sec: float) -> Dict[str, float]:
        """Get the heading, tilt, and roll for current position based on 
        elapsed time.

        Arguments
            elapsed_time_sec: elapsed time since launch (seconds)
        """
        current_position_dict = self.get_current_position(elapsed_time_sec)
        current_bearing_deg = self.compute_current_bearing(
            position_lat_deg=current_position_dict['lat_deg'],
            position_lon_deg=current_position_dict['lon_deg'],
        )
        current_tilt_deg = geo.convert_trig_to_compass_angle(
            trig_angle=self.initial_launch_angle_deg,
            radians=False,
        )
        current_orientation_dict = {
            'bearing_deg':current_bearing_deg,
            'tilt_deg':current_tilt_deg,
            'roll_deg':0,
        }
        return current_orientation_dict
    
#    def compute_current_vertical_velocity(self, elapsed_time_sec: float) -> float:
#        """Compute vertical velocity (km/s) given elapsed time in seconds since
#        targeted missile launch.
#        
#        Arguments
#            elapsed_time_sec: Elapsed time since launch (in seconds)
#        """
#        if self.initial_vert_vel_km_per_sec is None:
#            self.set_initial_vertical_velocity()
#        current_vert_vel_km_per_sec = (
#            self.initial_vert_vel_km_per_sec 
#            + GRAVITY_ACCEL_KM_PER_S2 * elapsed_time_sec
#        )
#        return current_vert_vel_km_per_sec

    def set_initial_launch_velocity(
        self,
        initial_launch_vel_km_per_sec: float,
    ) -> None:
        """Compute and set initial launch velocity (km/sec) after instantiation."""
        self.initial_launch_vel_km_per_sec = initial_launch_vel_km_per_sec

    def set_intercept_time(self) -> None:
        """Compute and set the time of intercept in seconds after targeted missile (TM)
        launch, given intercept distance from targeted missile aimpoint (TMAP)."""
        self.intercept_seconds_after_TM_launch = (
            (self.targeted_missile.dist_to_target_km - self.intercept_ground_dist_from_TMAP_km)
            / self.targeted_missile.horiz_vel_km_per_sec
        )

    def set_intercept_position(self) -> None:
        """Compute and set the latitude, longitude, and altitude of intercept location."""            
        self.intercept_position_dict = self.targeted_missile.get_current_position(
            elapsed_time_sec=self.intercept_seconds_after_TM_launch
        )

    def set_aimpoint(self) -> None:
        """Set aimpoint latitude and longitude."""
        self.AP_latlon_deg = [
            self.intercept_position_dict['lat_deg'],
            self.intercept_position_dict['lon_deg']
        ]

    def set_initial_launch_angle(self) -> None:
        """Compute and set initial launch angle (degrees)."""
        self.initial_launch_angle_deg = geo.rad_to_deg(
            np.arccos(
                self.intercept_ground_dist_from_IMLP_km 
                / self.intercept_surface_to_air_dist_km
            )
        )
        print('Initial launch angle is '+
              f'{round(self.initial_launch_angle_deg, 2)} degrees.')

    def set_intercept_ground_dist_from_IMLP(self) -> None:
        """Compute and set the ground distance in kilometers from the interceptor
        missile launch point (IMLP) to the point of intercept."""
        self.intercept_ground_dist_from_IMLP_km = geo.calculate_great_circle_distance(
            origin_lat_deg=self.LP_latlon_deg[0],
            origin_lon_deg=self.LP_latlon_deg[1],
            dest_lat_deg=self.intercept_position_dict['lat_deg'],
            dest_lon_deg=self.intercept_position_dict['lon_deg'],
        )

    def set_intercept_surface_to_air_distance(self) -> None:
        """Compute and set the straight-line distance between interceptor launch
        point and intercept location."""
        interceptor_LP_vector = geo.convert_lat_lon_alt_to_nvector(
            lat_deg=self.LP_latlon_deg[0],
            lon_deg=self.LP_latlon_deg[1],
        )
        intercept_position_vector = geo.convert_lat_lon_alt_to_nvector(
            lat_deg=self.intercept_position_dict['lat_deg'],
            lon_deg=self.intercept_position_dict['lon_deg'],
            alt_km=self.intercept_position_dict['alt_km'],
        )
        self.intercept_surface_to_air_dist_km = geo.calculate_magnitude_dist_bt_vectors(
            interceptor_LP_vector, intercept_position_vector,
        )
    
    def set_intercept_flight_time(self) -> None:
        """Compute and set total flight time for interceptor missile (seconds)."""
        self.intercept_flight_time_seconds = (
            self.intercept_surface_to_air_dist_km / self.initial_launch_vel_km_per_sec
        )

    def set_intercept_launch_time(self) -> None:
        """Compute and set launch time of interceptor missile based on 
        distance to intercept point and interceptor launch velocity."""
        self.intercept_launch_time_seconds = ( #TODO: this isn't correct; should be intercept flight time, not launch time
            self.intercept_seconds_after_TM_launch - self.intercept_flight_time_seconds
        )

    def set_horizontal_velocity(self) -> None:
        """Compute and set horizontal velocity (km/sec).
        Note that horizontal velocity is constant over entire trajectory."""
        self.horiz_vel_km_per_sec = (
            self.intercept_ground_dist_from_IMLP_km / self.intercept_flight_time_seconds
        )

    def create_kml_trajectory(self) -> None:
        """Create missile trajectory in KML format."""
        kml_trajectory_sim = KMLTrajectorySim(
            data=self.trajectory_data,
            collada_model_link=self.collada_model_link,
            collada_model_scale=self.collada_model_scale,
        )
        kml_trajectory_sim.create_trajectory()
        self.kml_trajectory = kml_trajectory_sim.kml
        
#TODO: find out why Missile 1 isn't being intercepted at proper time  (on correct trajectory; interceptor not moving quickly enough, launching early enough)