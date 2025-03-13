"""Main execution for missile intercept model."""

# Import packages
from datetime import datetime
import os
from typing import Dict

import pandas as pd

import simplekml

from src.missiles_ballistic import BallisticMissile
from src.utils_kml import save_kmz

# Define functions
def main(config_path: str) -> None:
    """Main execution for missile intercept model."""
    config_ballistic = parse_config(config_path, sheet_name='ballistic')
    config_interceptor = parse_config(config_path, sheet_name='interceptor')
    for group, sim_params_dict in config_ballistic.items():
        kml = simplekml.Kml()
        for sim, params in sim_params_dict.items():
            missile = BallisticMissile(params)
            missile.build()
            missile.launch()
            kml = missile.create_kml_trajectory(kml)
        save_kmz(
            kml=kml,
            output_dir='kml',
            output_file_name=group,
            attachment_dir='blender',
            attachment_files_list=['test_missile.dae'],
        )

def parse_config(path: str, sheet_name: str) -> Dict:
    """Parse config file to create nested dict {group:{simulation:{param:value}}}"""
    config = pd.read_excel(path, sheet_name=sheet_name)
    drop_cols = [
        col for col in config.columns if config[col].isnull().all()
        or 'Dtype' in col or 'Description' in col
    ]
    config = config.drop(columns=drop_cols).set_index('Parameter').T
    nested_config = {}
    for group in config['group_name'].unique():
        group_config = config.loc[config['group_name'] == group].T.to_dict()
        group_dict = {}
        for sim, params in group_config.items():
            params['LP_latlon_deg'] = (params['LP_lat_deg'], params['LP_lon_deg'])
            params['collada_model_path'] = os.path.join(
                params['collada_model_dir'], params['collada_model_file']
            )
            # Ballistic-specific params
            if sheet_name == 'ballistic':
                params['AP_latlon_deg'] = (params['AP_lat_deg'], params['AP_lon_deg'])
                params['launch_time'] = datetime.combine(
                    params['launch_date'], params['launch_time_UTC'],
                )
            group_dict[sim] = params
        nested_config[group] = {**group_dict}
    return nested_config


if __name__ == '__main__':
    config_path = 'config/config.xlsx'
    main(config_path)
