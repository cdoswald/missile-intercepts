"""KMLTrajectory and KMLCamera classes."""

#TODO: Define styles (possibly in utils)
#TODO: Add stylemap (in utils)
#TODO: Linestring and point altitudes
#TODO: Add point for final timestep
#TODO: Check hemisphere coordinates
#TODO: Add timestamps
#TODO: Add save KMZ functions to utils
#TODO: Add camera classes
#TODO: Add converter classes?

# Import packages
from collections import OrderedDict
import inspect
import os
import sys
from typing import Optional

import numpy as np
import pandas as pd

import simplekml

# Import local modules
scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(scriptdir)
sys.path.insert(0, parentdir)
import geo_utils as geo
import kml_utils

# Define constants
EARTH_RADIUS_KM = 6378

# Define classes
class KMLTrajectory():
    """Base class for creating a missile trajectory KML file."""
    
    def __init__(
        self,
        data: Optional[pd.DataFrame] = None,
        time_col_name: str = 'time_sec',
        lat_col_name: str = 'lat_deg',
        lon_col_name: str = 'lon_deg',
        altitude_col_name: str = 'alt_km',
    ) -> None:
        """Instantiate KMLTrajectory class.
        
        Arguments
            data: pandas DataFrame containing trajectory data
            time_col_name: name of time column in data
            lat_col_name: name of latitude column in data
            lon_col_name: name of longitude column in data
            altitude_col_name: name of altitude column in data
        """
        self.data = data.sort_values([time_col_name]).reset_index(drop=True)
        self.time_col_name = time_col_name
        self.lat_col_name = lat_col_name
        self.lon_col_name = lon_col_name
        self.altitude_col_name = altitude_col_name
        self.kml = simplekml.Kml()

    def create_trajectory(self) -> None:
        """Create missile trajectory KML objects."""
        for idx in self.data.index:
            position_dict = self.data.loc[idx].to_dict()
            if idx != self.data.index.max():
                next_position_dict = self.data.loc[idx+1].to_dict()
                kml_utils.create_kml_linestring(
                    fol=self.kml,
                    lonlat_list=[
                        (position_dict[self.lon_col_name], position_dict[self.lat_col_name]),
                        (next_position_dict[self.lon_col_name], next_position_dict[self.lat_col_name]),
                    ],
                    style=simplekml.Style(), #TODO
                    label='',
                    close_linestring=False,
                )
                kml_utils.create_kml_point(
                    fol=self.kml,
                    lat=position_dict[self.lat_col_name],
                    lon=position_dict[self.lon_col_name],
                    style=simplekml.Style(), #TODO
                    pnt_label=f'Time: {position_dict[self.time_col_name]}',
                    timespan_begin='',
                    timespan_end='',
                )
