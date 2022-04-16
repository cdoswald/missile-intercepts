"""
Ballistic missile classes.

Contents:
    Public classes:
        BallisticMissile

    Private classes:
        _BallisticMissileBuilder (component of BallisticMissile)
        _BallisticMissileLauncher (component of BallisticMissile)
        _BallisticMissileSimulator (component of BallisticMissile)
"""
# Import packages
from collections import OrderedDict
from typing import Dict, Optional, Tuple, Type

import numpy as np
import pandas as pd

from missile_abstract import Missile
from kml_classes import KMLTrajectorySim
import geo_utils as geo
import utils as utl

# Get constants
constants = utl.get_constants()

# Define classes
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
        params: Optional[Dict] = None,
        LP_latlon_deg: Optional[Tuple[float, float]] = None,
        AP_latlon_deg: Optional[Tuple[float, float]] = None,
        time_to_target_sec: Optional[float] = None,
        intercept_ground_dist_from_TMAP_km: Optional[float] = None,
        collada_model_link: str = "../COLLADA/test_collada.dae",
        collada_model_scale: float = 200,
    ) -> None:
        """Instantiate BallisticMissile class.
        
        Arguments
            params: dict of parameter values
            LP_latlon_deg: tuple of launchpoint (latitude, longitude) in degrees
            AP_latlon_deg: tuple of aimpoint (latitutde, longitude) in degrees
            position: tuple of missile latitude, longitude, and altitude for timestep
            orientation: tuple of missile heading, tilt, and roll for timestep
    

            time_to_target_sec: Total time (in seconds) for missile to travel
                from launchpoint to aimpoint
            collada_model_link: path or URL to 3D model in COLLADA format (.dae)
            collada_model_scale: scale factor for all 3D model axes (x, y, and z)
        """
        super(BallisticMissile, self).__init__(
            params, LP_latlon_deg, AP_latlon_deg
        )
        self.build_data = None
        self.launch_data = None


class _BallisticMissileBuilder():
    """A component class of BallisticMissile that calculates all static
    characteristics of the missile trajectory.
    
    Attributes:
        params: dict of user-defined parameter values
        LP_latlon_deg: tuple of launchpoint (latitude, longitude) in degrees
        AP_latlon_deg: tuple of aimpoint (latitutde, longitude) in degrees
        build_data: dict of static characteristics of missile trajectory
    
    Methods:
        get_build_data
        comput_distance_to_target
        compute_initial_bearing
        compute_time_to_target
        compute_initial_vertical_velocity
        compute_initial_launch_velocity
        compute_initial_launch_angle
    """
    
    def __init__(
        self,
        params: Dict,
        LP_latlon_deg: Tuple[float, float],
        AP_latlon_deg: Tuple[float, float],
    ) -> None:
        """Instantiate _BallisticMissileBuilder."""
        self.params = params
        self.LP_latlon_deg = LP_latlon_deg
        self.AP_latlon_deg = AP_latlon_deg
        self.build_data = None

    def get_build_data(self) -> Dict:
        """Compute all static characteristics of ballistic missile trajectory:
            - Distance to target (km)
            - Time-to-target (seconds)
            - Horizontal velocity (km/sec)
            - Initial vertical velocity (km/sec)
            - Initial launch velocity (km/sec)
            - Initial bearing (degrees)
            - Initial launch angle (degrees)
        """
        dist_to_target_km = self.compute_distance_to_target()
        initial_bearing_deg = self.compute_initial_bearing()
        horizontal_velocity_km_sec = self.params['horizontal_velocity_km_sec']
        time_to_target_sec = (
            self.compute_time_to_target(horizontal_velocity_km_sec)
        )
        initial_vertical_velocity = (
            self.compute_initial_vertical_velocity(time_to_target_sec)
        )
        initial_launch_velocity = self.compute_initial_launch_velocity(
            horizontal_velocity_km_sec, initial_vertical_velocity,
        )
        initial_launch_angle = self.compute_initial_launch_angle(
            horizontal_velocity_km_sec, initial_vertical_velocity,
        )
        return {
            'dist_to_target_km':dist_to_target_km,
            'initial_bearing_deg':initial_bearing_deg,
            'horizontal_velocity_km_sec':horizontal_velocity_km_sec,
            'time_to_target_sec':time_to_target_sec,
            'initial_vertical_velocity':initial_vertical_velocity,
            'initial_launch_velocity':initial_launch_velocity,
            'initial_launch_angle':initial_launch_angle,
        }

    def compute_distance_to_target(self) -> float:
        """Compute great-circle distance (km) between launchpoint and aimpoint."""
        return geo.calculate_great_circle_distance(
            self.LP_latlon_deg[0], self.LP_latlon_deg[1],
            self.AP_latlon_deg[0], self.AP_latlon_deg[1],
        )
    
    def compute_initial_bearing(self) -> float:
        """Compute forward azimuth/initial bearing (degrees, clockwise from 
        North) from launchpoint to aimpoint."""
        return geo.calculate_initial_bearing(
            self.LP_latlon_deg[0], self.LP_latlon_deg[1],
            self.AP_latlon_deg[0], self.AP_latlon_deg[1],
        )

    def compute_time_to_target(self, horizontal_velocity_km_sec: float) -> float:
        """Given constant horizontal velocity (km/sec), calculate time-to-target
        (seconds).
        
        Arguments:
            horizontal_velocity_km_sec: constant horizontal velocity (km/sec)
        """
        return self.compute_distance_to_target() / horizontal_velocity_km_sec

    def compute_initial_vertical_velocity(self, time_to_target_sec: float) -> float:
        """Compute initial vertical velocity (km/sec) as time-to-apogee (seconds)
        multiplied by gravitational acceleration (km/sec^2).

        Arguments:
            time_to_target_sec: missile time-to-target (seconds)
        """
        time_to_apogee_sec = time_to_target_sec * 0.5
        initial_vertical_velocity_km_sec = (
            time_to_apogee_sec * abs(constants['GRAVITY_ACCEL_KM_PER_S2'])
        )
        return initial_vertical_velocity_km_sec

    def compute_initial_launch_velocity(
        self,
        horizontal_velocity_km_sec: float,
        initial_vertical_velocity_km_sec: float,
    ) -> float:
        """Compute initial launch velocity (km/sec) using horizontal and vertical
        components of velocity (km/sec).

        Arguments:
            horizontal_velocity_km_sec: constant horizontal velocity (km/sec)
            initial_vertical_velocity_km_sec: vertical velocity (km/sec) at time
                of missile launch
        """
        return np.sqrt(
            horizontal_velocity_km_sec**2 + initial_vertical_velocity_km_sec**2
        ) #TODO: verify initial launch velocity less than Earth escape velocity

    def compute_initial_launch_angle(
        self,
        horizontal_velocity_km_sec: float,
        initial_vertical_velocity_km_sec: float,
    ) -> float:
        """Compute initial launch angle (degrees) using horizontal and vertical
        components of velocity (km/sec).

        Arguments:
            horizontal_velocity_km_sec: constant horizontal velocity (km/sec)
            initial_vertical_velocity_km_sec: vertical velocity (km/sec) at time
                of missile launch
        """
        return geo.rad_to_deg(np.arctan(
            initial_vertical_velocity_km_sec / horizontal_velocity_km_sec
        ))


class _BallisticMissileLauncher():
    """A component class of BallisticMissile that calculates all dynamic
    characteristics of the missile trajectory.
    
    Attributes:
        params: dict of user-defined parameter values
        LP_latlon_deg: tuple of launchpoint (latitude, longitude) in degrees
        AP_latlon_deg: tuple of aimpoint (latitutde, longitude) in degrees
        build_data:
    
    Methods:
        
    """
    
    def __init__(
        self,
        params: Dict,
        LP_latlon_deg: Tuple[float, float],
        AP_latlon_deg: Tuple[float, float],
    ) -> None:
        """Instantiate _BallisticMissileLauncher."""
        self.params = params
        self.LP_latlon_deg = LP_latlon_deg
        self.AP_latlon_deg = AP_latlon_deg
        self.launch_data = None
    

    
    def get_launch_data(self) -> Dict:
        """Record missile position (latitude, longitude, altitude) and orientation
        (heading, tilt, and roll) for each timestep from launch until impact.
        """
         
        
        
        
        self.intercept_ground_dist_from_TMAP_km = intercept_ground_dist_from_TMAP_km
        self.collada_model_link = collada_model_link
        self.collada_model_scale = collada_model_scale
        self.intercept_seconds_after_launch = None
            
        
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



    # def compute_current_bearing(
    #     self,
    #     position_lat_deg: float,
    #     position_lon_deg: float,
    # ) -> float:
    #     """Compute forward azimuth/initial bearing from current location to 
    #     aimpoint. Bearing measured in degrees, clockwise from North."""
    #     current_bearing_deg = geo.calculate_initial_bearing(
    #         origin_lat_deg=position_lat_deg,
    #         origin_lon_deg=position_lon_deg,
    #         dest_lat_deg=self.AP_latlon_deg[0],
    #         dest_lon_deg=self.AP_latlon_deg[1],
    #         )
    #     return current_bearing_deg