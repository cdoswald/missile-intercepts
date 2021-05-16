"""Run Ballistic Missile Intercept Model."""

# Import packages
import inspect
import json
import os
import sys

# Import local modules
from missile_classes import BallisticMissile, TerminalPhaseInterceptor

script_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.join(script_dir, 'Utils'))
import kml_utils

# Define functions
def main(config_path: str) -> None:
    with open(config_path, 'r') as file:
        config = json.load(file)
    for missile_name, params in config.items():
        # Create ballistic missile
        ballistic_missile = BallisticMissile(
            LP_lat_deg=params['ballistic_launchpoint_latlon'][0],
            LP_lon_deg=params['ballistic_launchpoint_latlon'][1],
            AP_lat_deg=params['ballistic_aimpoint_latlon'][0],
            AP_lon_deg=params['ballistic_aimpoint_latlon'][1],
            time_to_target_sec=params['ballistic_time_to_target_sec'],
            collada_model_link=params['ballistic_COLLADA_model_link'],
            collada_model_scale=params['ballistic_COLLADA_model_scale'],
            intercept_ground_dist_from_TMAP_km=params['intercept_ground_dist_from_aimpoint_km'],
            )
        ballistic_missile.build()
        ballistic_missile.launch()
        ballistic_missile.create_kml_trajectory()
        # Create interceptor missile
        interceptor = TerminalPhaseInterceptor(
            IMLP_lat_deg=params['interceptor_launchpoint_latlon'][0],
            IMLP_lon_deg=params['interceptor_launchpoint_latlon'][1],
            max_ground_range_km=params['interceptor_max_ground_range_km'],
            initial_launch_vel_km_per_sec=params['initial_launch_vel_km_per_sec'],
            collada_model_link=params['interceptor_COLLADA_model_link'],
            collada_model_scale=params['interceptor_COLLADA_model_scale'],
            targeted_missile=ballistic_missile,
            intercept_ground_dist_from_TMAP_km=params['intercept_ground_dist_from_aimpoint_km'],
        )
        interceptor.build()
        interceptor.launch()
        interceptor.create_kml_trajectory()
        # Save KML files
        kml_utils.save_kmz(
            kml=ballistic_missile.kml_trajectory,
            output_dir=r'..\KML',
            output_file_name=missile_name,
            attachment_dir=r'..\COLLADA',
            attachment_files_list=['test_collada.dae'],
        )
        kml_utils.save_kmz(
            kml=interceptor.kml_trajectory,
            output_dir=r'..\KML',
            output_file_name=f'{missile_name}_Interceptor',
            attachment_dir=r'..\COLLADA',
            attachment_files_list=['test_collada.dae'],
        )
        ballistic_missile.trajectory_data.to_csv(f'{missile_name}_traj_data.csv')
        interceptor.trajectory_data.to_csv(f'{missile_name}_interceptor_traj_data.csv')

if __name__ == '__main__':
    main(config_path=r'..\Config Files\config.json')
