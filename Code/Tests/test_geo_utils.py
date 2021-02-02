"""Unit tests for geo_utils.py."""

# Import packages
import inspect
import os
import sys

import numpy as np

# Import local modules
script_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(script_dir)
utils_dir = os.path.join(parent_dir, 'Utils')
sys.path.insert(0, utils_dir)
import geo_utils as geo

# Define tests
def test_polar_angle_to_bearing():
    """Test that polar_angle_to_bearing function correctly converts polar angle 
    (measured counterclockwise from East) to bearing (measured clockwise from North).
    """
    conversions_dict = {
        'degrees':[
            {'polar_angle':0, 'bearing':90},
            {'polar_angle':90, 'bearing':0},
            {'polar_angle':180, 'bearing':270},
            {'polar_angle':270, 'bearing':180},
            {'polar_angle':360, 'bearing':90},
        ],
        'radians':[
            {'polar_angle':0, 'bearing':(np.pi/2)},
            {'polar_angle':(np.pi/2), 'bearing':0},
            {'polar_angle':(np.pi), 'bearing':(3/2*np.pi)},
            {'polar_angle':(3/2*np.pi), 'bearing':(np.pi)},
            {'polar_angle':(2*np.pi), 'bearing':(np.pi/2)},
        ]
    }
    errors_list = []
    for unit, conversions_list in conversions_dict.items():
        radians_bool = (unit == 'radians')
        for conversion_dict in conversions_list:
            converted_val = geo.polar_angle_to_bearing(
                polar_angle=conversion_dict['polar_angle'],
                radians=radians_bool
            )
            if converted_val != conversion_dict['bearing']:
                errors_list.append('Incorrect conversion for '+
                    f'{conversion_dict["polar_angle"]} {unit}.'
                )
    assert not errors_list, 'Errors occurred: \n{}'.format('\n'.join(errors_list))

def test_calculate_great_circle_distance():
    """Test that calculate_great_circle_distance function correctly 
    calculates the great circle distance between locations in all hemispheres.
    """
    margin_of_error_allowed = 0.002
    latlon_deg_dict = {
        'Denver':[39.7392, -104.9903],
        'Amman':[31.9539, 35.9106],
        'Sydney':[-33.8688, 151.2093],
        'Santiago':[-33.4489, -70.6693],
    }
    distances_km_dict = {
        'Denver_to_Amman':11076,
        'Denver_to_Sydney':13398,
        'Denver_to_Santiago':8865,
        'Amman_to_Denver':11076,
        'Amman_to_Sydney':14067,
        'Amman_to_Santiago':13289,
        'Sydney_to_Denver':13398,
        'Sydney_to_Amman':14067,
        'Sydney_to_Santiago':11340,
        'Santiago_to_Denver':8865,
        'Santiago_to_Amman':13289,
        'Santiago_to_Sydney':11340,
    }
    errors_list = []
    for origin_city, origin_latlon_deg in latlon_deg_dict.items():
        for dest_city, dest_latlon_deg in latlon_deg_dict.items():
            if origin_city == dest_city:
                continue
            else:
                calculated_dist_km = geo.calculate_great_circle_distance(
                    origin_lat_deg=origin_latlon_deg[0],
                    origin_lon_deg=origin_latlon_deg[1],
                    dest_lat_deg=dest_latlon_deg[0],
                    dest_lon_deg=dest_latlon_deg[1],
                )
                route_key = f'{origin_city}_to_{dest_city}'
                actual_dist_km = distances_km_dict[route_key]
                margin_of_error_actual = (
                    abs(calculated_dist_km - actual_dist_km) / actual_dist_km
                )
                if margin_of_error_actual > margin_of_error_allowed:
                    errors_list.append('Calculated distance for '+
                    f'{route_key.replace("_", " ")} exceeds a margin of error '+
                    f'of {margin_of_error_allowed * 100}%.'
                )
    assert not errors_list, 'Errors occurred: \n{}'.format('\n'.join(errors_list))

if __name__ == '__main__':
    test_polar_angle_to_bearing()
    test_calculate_great_circle_distance()
