"""Main execution for missile intercept model."""

# Import packages
from datetime import datetime
import os
from typing import Dict

import pandas as pd

import simplekml

from missiles_ballistic import BallisticMissile
from utils_kml import save_kmz

# Define functions
def main() -> None:
    """Main execution for missile intercept model."""
    config = parse_config('../Config/config.xlsx')
    for group, sim_params_dict in config.items():
        kml = simplekml.Kml()
        for sim, params in sim_params_dict.items():
            missile = BallisticMissile(params)
            missile.build()
            missile.launch()
            kml = missile.create_kml_trajectory(kml)
        save_kmz(
            kml=kml,
            output_dir='../kml',
            output_file_name=group,
            attachment_dir='../blender',
            attachment_files_list=['test_missile.dae'],
        )

def parse_config(path: str) -> Dict:
    """Parse config file to create nested dict {group:{simulation:{param:value}}}"""
    config = pd.read_excel(path, sheet_name='config')
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
            params['AP_latlon_deg'] = (params['AP_lat_deg'], params['AP_lon_deg'])
            params['collada_model_path'] = os.path.join(
                params['collada_model_dir'], params['collada_model_file']
            )
            params['launch_time'] = datetime.combine(
                params['launch_date'], params['launch_time_UTC'],
            )
            group_dict[sim] = params
        nested_config[group] = {**group_dict}
    return nested_config

        
if __name__ == '__main__':
    main()
