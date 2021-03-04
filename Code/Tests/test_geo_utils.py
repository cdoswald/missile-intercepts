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
def test_convert_trig_to_compass_angle():
    """Test that convert_trig_to_compass_angle function correctly converts 
    trigonometric angle (measured counterclockwise from East) to compass angle
    (measured clockwise from North).
    """
    test_cases = {
        'degrees':[
            {'trig_angle':0, 'compass_angle':90},
            {'trig_angle':90, 'compass_angle':0},
            {'trig_angle':180, 'compass_angle':270},
            {'trig_angle':270, 'compass_angle':180},
            {'trig_angle':360, 'compass_angle':90},
        ],
        'radians':[
            {'trig_angle':0, 'compass_angle':(np.pi/2)},
            {'trig_angle':(np.pi/2), 'compass_angle':0},
            {'trig_angle':(np.pi), 'compass_angle':(3/2*np.pi)},
            {'trig_angle':(3/2*np.pi), 'compass_angle':(np.pi)},
            {'trig_angle':(2*np.pi), 'compass_angle':(np.pi/2)},
        ]
    }
    errors_list = []
    for unit, conversions_list in test_cases.items():
        radians_bool = (unit == 'radians')
        for conversion_dict in conversions_list:
            converted_val = geo.convert_trig_to_compass_angle(
                trig_angle=conversion_dict['trig_angle'],
                radians=radians_bool
            )
            if converted_val != conversion_dict['compass_angle']:
                errors_list.append('Incorrect conversion for '+
                    f'{conversion_dict["trig_angle"]} {unit}.'
                )
    assert not errors_list, 'Errors occurred: \n{}'.format('\n'.join(errors_list))

def test_convert_latlon_to_nvector():
    """Test that convert_latlon_to_nvector function correctly converts a
    latitude-longitude pair (in decimal degrees) to an orthogonal (normal)
    vector with coordiates <x, y, z>.
    """
    test_cases = {
        'North_0_East_0':{'latlon_deg':(0, 0), 'nvector':(1, 0, 0)},
        'North_0_East_90':{'latlon_deg':(0, 90), 'nvector':(0, 1, 0)},
        'North_0_East_180':{'latlon_deg':(0, 180), 'nvector':(-1, 0, 0)},
        'North_0_West_90':{'latlon_deg':(0, -90), 'nvector':(0, -1, 0)},
        'North_0_West_180':{'latlon_deg':(0, -180), 'nvector':(-1, 0, 0)},
        'North_90_East_0':{'latlon_deg':(90, 0), 'nvector':(0, 0, 1)},
        'South_90_East_0':{'latlon_deg':(-90, 0), 'nvector':(0, 0, -1)},
    }
    errors_list = []
    for direction, conversions_dict in test_cases.items():
        latlon_deg = conversions_dict['latlon_deg']
        n_vector = geo.convert_latlon_to_nvector(
            lat_deg=latlon_deg[0], lon_deg=latlon_deg[1]
        )
        if len(n_vector) != 3:
            errors_list.append(f'Normal vector for test case "{direction}" '+
                f'contains {len(n_vector)} coordinates.')
        if tuple([round(x, 10) for x in n_vector]) != conversions_dict['nvector']:
            errors_list.append(f'Incorrect conversion for test case "{direction}".')
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

def test_calculate_great_circle_distance_vec():
    """Test that calculate_great_circle_distance_vec function correctly 
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
                calculated_dist_km = geo.calculate_great_circle_distance_vec(
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
    test_convert_trig_to_compass_angle()
    test_convert_latlon_to_nvector()
    test_calculate_great_circle_distance()
    test_calculate_great_circle_distance_vec()
