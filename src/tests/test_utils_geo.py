"""
Unit tests for utils_geo.py.
"""
# Import packages
import numpy as np

from ..utils import get_constants
from ..utils_geo import (
    convert_trig_to_compass_angle,
    convert_lat_lon_alt_to_nvector,
    calculate_magnitude_dist_bt_vectors,
    calculate_great_circle_distance,
    calculate_great_circle_distance_vec
)

# Get constants
constants = get_constants()

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
            converted_val = convert_trig_to_compass_angle(
                trig_angle=conversion_dict['trig_angle'],
                radians=radians_bool
            )
            if converted_val != conversion_dict['compass_angle']:
                errors_list.append('Incorrect conversion for '+
                    f'{conversion_dict["trig_angle"]} {unit}.'
                )
    assert not errors_list, 'Errors occurred: \n{}'.format('\n'.join(errors_list))

def test_convert_lat_lon_alt_to_nvector():
    """Test that convert_lat_lon_alt_to_nvector function correctly converts a
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
        n_vector = convert_lat_lon_alt_to_nvector(
            lat_deg=latlon_deg[0], lon_deg=latlon_deg[1]
        )
        if len(n_vector) != 3:
            errors_list.append(f'Normal vector for test case "{direction}" '+
                f'contains {len(n_vector)} coordinates.')
        if (
            tuple([round(x, 10) for x in n_vector]) !=
            tuple([constants['EARTH_RADIUS_KM'] * x for x in conversions_dict['nvector']])
        ):
            errors_list.append(f'Incorrect conversion for test case "{direction}".')
    assert not errors_list, 'Errors occurred: \n{}'.format('\n'.join(errors_list))

def test_calculate_magnitude_dist_bt_vectors():
    """Test that calculate_magnitude_dist_bt_vectors function correctly calculates
    the magnitude of the Euclidean distance between two vectors in R3.
    """
    test_cases = {
        'test1':{'vec1':(0, 0, 0), 'vec2':(0, 0, 0), 'magnitude_dist':0},
        'test2':{'vec1':(1, 1, 1), 'vec2':(0, 0, 0), 'magnitude_dist':np.sqrt(3)},
        'test3':{'vec1':(0, 0, 0), 'vec2':(3, 2, 1), 'magnitude_dist':np.sqrt(14)},
        'test4':{'vec1':(2, 3, 4), 'vec2':(4, 5, 6), 'magnitude_dist':np.sqrt(12)},
        'test5':{'vec1':(-1, -1, -1), 'vec2':(0, 0, 0), 'magnitude_dist':np.sqrt(3)},
        'test6':{'vec1':(0, 0, 0), 'vec2':(-3, -2, -1), 'magnitude_dist':np.sqrt(14)},
        'test7':{'vec1':(-2, -3, -4), 'vec2':(-4, -5, -6), 'magnitude_dist':np.sqrt(12)},
    }
    errors_list = []
    for test_num, vectors_dict in test_cases.items():
        calculated_dist = calculate_magnitude_dist_bt_vectors(
            vectors_dict['vec1'], vectors_dict['vec2'],
        )
        if calculated_dist != vectors_dict['magnitude_dist']:
            errors_list.append(f'Incorrect distance magnitude calculation for {test_num}.')
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
                calculated_dist_km = calculate_great_circle_distance(
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
                calculated_dist_km = calculate_great_circle_distance_vec(
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
    test_convert_lat_lon_alt_to_nvector()
    test_calculate_magnitude_dist_bt_vectors()
    test_calculate_great_circle_distance()
    test_calculate_great_circle_distance_vec()
