"""Run Ballistic Missile Intercept Model."""

# Import packages
import inspect
import json
import os
import sys

# Import local modules
from missile_classes import BallisticMissile

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
            launch_lat_deg=params['launchpoint_latlon'][0],
            launch_lon_deg=params['launchpoint_latlon'][1],
            aimpoint_lat_deg=params['aimpoint_latlon'][0],
            aimpoint_lon_deg=params['aimpoint_latlon'][1],
            time_to_target_sec=params['time_to_target_sec'],
            collada_model_link=params['COLLADA_model_link'],
            collada_model_scale=params['COLLADA_model_scale'],
            )
        ballistic_missile.build()
        ballistic_missile.launch()
        ballistic_missile.create_kml_trajectory()
        kml_utils.save_kmz(
            kml=ballistic_missile.kml_trajectory,
            output_dir=r'..\KML',
            output_file_name=missile_name,
            attachment_dir=r'..\COLLADA',
            attachment_files_list=['test_collada.dae'],
        )

if __name__ == '__main__':
    main(config_path=r'..\Config Files\config.json')
