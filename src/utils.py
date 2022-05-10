"""Utility functions."""

# Import packages
import json
from typing import Dict

import numpy as np

# Constants
def get_constants() -> Dict:
    """Calculate and return dictionary of constants."""
    EARTH_RADIUS_KM = 6378
    EARTH_MASS_KG = 5.9722 * (10**24)
    GRAV_CONSTANT_M3_PER_KG_S2 = 6.673 * (10**-11)
    EARTH_STD_GRAV_PARAM_M3_PER_S2 = GRAV_CONSTANT_M3_PER_KG_S2 * EARTH_MASS_KG
    EARTH_ESCAPE_VELOCITY_KM_PER_S = (
        np.sqrt(2 * EARTH_STD_GRAV_PARAM_M3_PER_S2 / (EARTH_RADIUS_KM*1000)) 
        / 1000
    )
    return {
        'EARTH_RADIUS_KM':EARTH_RADIUS_KM,
        'EARTH_MASS_KG':EARTH_MASS_KG,
        'GRAVITY_ACCEL_KM_PER_S2':(-0.0098),
        'GRAV_CONSTANT_M3_PER_KG_S2':GRAV_CONSTANT_M3_PER_KG_S2,
        'EARTH_STD_GRAV_PARAM_M3_PER_S2':EARTH_STD_GRAV_PARAM_M3_PER_S2,
        'EARTH_ESCAPE_VELOCITY_KM_PER_S':EARTH_ESCAPE_VELOCITY_KM_PER_S,
        'KML_TIME_FORMAT':'%Y-%m-%dT%H:%M:%SZ',
    }

## I/O
def load_json(filepath:str) -> Dict:
    """Load JSON file."""
    with open(filepath, 'r') as file:
        data = json.load(file)
    return data
