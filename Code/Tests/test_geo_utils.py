"""Unit tests for geo_utils.py."""

# Import packages
import inspect
import os
import sys

import numpy as np

# Import local modules
scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(scriptdir)
geo_utils_dir = os.path.join(parentdir, 'Code')
sys.path.insert(0, geo_utils_dir)
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

if __name__ == '__main__':
    test_polar_angle_to_bearing()
