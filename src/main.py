"""Main execution for missile intercept model."""

# Import packages
from datetime import datetime
import os
from typing import Dict

import pandas as pd

import simplekml

from src.missiles_ballistic import BallisticMissile
from src.missiles_interceptor import TerminalInterceptor
from src.utils_kml import save_kmz


def main(config_path: str) -> None:
    """Main execution for missile intercept model."""
    config_ballistic = parse_config(config_path, sheet_name='ballistic')
    config_interceptor = parse_config(config_path, sheet_name='interceptor')
    all_group_names = set(list(config_ballistic.keys()) + list(config_interceptor.keys()))
    for group_name in all_group_names:
        kml = simplekml.Kml()
        sim_params_dict_ballistic = config_ballistic[group_name]
        sim_params_dict_interceptor = config_interceptor[group_name]
        for sim, params in sim_params_dict_ballistic.items():
            missile_intercept_time = None
            missile = BallisticMissile(params)
            missile.build()
            # Create trajectory for interceptor(s)
            for interceptor_sim, interceptor_params in sim_params_dict_interceptor.items():
                if params["missile_name"] in interceptor_params["intercept_missile_name"]:
                    interceptor = TerminalInterceptor(interceptor_params)
                    interceptor.set_intercept_target(missile)
                    interceptor.build()
                    interceptor.launch()
                    kml = interceptor.create_kml_trajectory(
                        kml,
                        interceptor_params["interceptor_name"]
                    )
                    # Update missile intercept time with earliest time
                    if missile_intercept_time is None:
                        missile_intercept_time = interceptor.intercept_time_sec
                    else:
                        missile_intercept_time = min(
                            missile_intercept_time, interceptor.intercept_time_sec
                        )
            # Create trajectory for ballistic missile
            if missile_intercept_time is not None:
                missile.launch(stoptime_sec=missile_intercept_time)
            else:
                missile.launch()
            kml = missile.create_kml_trajectory(kml, params["missile_name"])

        # Save group KML file
        save_kmz(
            kml=kml,
            output_dir='kml',
            output_file_name=group_name,
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
            # Ballistic missile-specific params
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
