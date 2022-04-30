"""Main execution for Ballistic Missile Intercept Model."""

# Import packages
from datetime import datetime

from missiles_ballistic import BallisticMissile
from utils_kml import save_kmz

# Define functions
def main() -> None:
    
    # Test
    params = {
        'LP_latlon_deg':(39.7392, -104.9903),
        'AP_latlon_deg':(41.1400, -104.8202),
        'horizontal_velocity_km_sec': 0.75,
        'launch_time':datetime.now(),
        'sim_start_time_buffer_sec':10,
        'sim_end_time_buffer_sec':10,
        'timestep_sec':0.25,
        'collada_model_link':'../COLLADA/test_missile.dae',
        'collada_model_scale':500,
    }
    missile1 = BallisticMissile(params)
    missile1.build()
    missile1.launch()
    missile1.convert_trajectory_to_kml()

    save_kmz(
        kml=missile1.kml_trajectory,
        output_dir='../KML',
        output_file_name='test',
        attachment_dir='../COLLADA',
        attachment_files_list=['test_missile.dae'],
    )
        
if __name__ == '__main__':
    main()


# collada_model_link: path or URL to 3D model in COLLADA format (.dae)
# collada_model_scale: scale factor for all 3D model axes (x, y, and z)
# launch_time: date and time of missile launch
