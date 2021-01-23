"""KMLTrajectory and KMLCamera classes."""

#TODO: Define styles (possibly in utils)
#TODO: Add stylemap (in utils)
#TODO: Add point for final timestep
#TODO: Check hemisphere coordinates
#TODO: Add save KMZ functions to utils
#TODO: Add camera classes
#TODO: Add converter classes?

# Import packages
from datetime import datetime, timedelta
import inspect
import os
import sys
from typing import Optional

import pandas as pd

import simplekml

# Import local modules
scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(scriptdir)
sys.path.insert(0, parentdir)
import kml_utils

# Define constants
EARTH_RADIUS_KM = 6378

# Define classes
class KMLTrajectory():
    """Base class for creating a missile trajectory KML file."""
    
    def __init__(
        self,
        data: Optional[pd.DataFrame] = None,
        time_colname: str = 'time_sec',
        latdeg_colname: str = 'lat_deg',
        londeg_colname: str = 'lon_deg',
        altm_colname: str = 'alt_m',
    ) -> None:
        """Instantiate KMLTrajectory class.
        
        Arguments
            data: pandas DataFrame containing trajectory data
            time_colname: name of time column in data
            latdeg_colname: name of latitude (degrees) column in data
            londeg_colname: name of longitude (degrees) column in data
            altm_colname: name of altitude (meters) column in data
        """
        self.data = data.sort_values([time_colname]).reset_index(drop=True)
        self.time_colname = time_colname
        self.latdeg_colname = latdeg_colname
        self.londeg_colname = londeg_colname
        self.altm_colname = altm_colname
        self.kml = simplekml.Kml()

    def create_trajectory(self) -> None:
        """Create KML points and linestrings tracing missile trajectory."""
        start_time = datetime.now()
        for idx in self.data.index:
            kml_folder = self.kml.newfolder(name=f'Point {idx}')
            position_dict = self.data.loc[idx].to_dict()
            timespan_begin = (
                start_time + timedelta(seconds=position_dict[self.time_colname])
            ).strftime('%Y-%m-%dT%H:%M:%SZ')
            if idx != self.data.index.max():
                next_position_dict = self.data.loc[idx+1].to_dict()
                pnt_timespan_end = (
                    start_time + timedelta(seconds=next_position_dict[self.time_colname])
                ).strftime('%Y-%m-%dT%H:%M:%SZ')
            else:
                pnt_timespan_end = ''
            # Add point indicating current location of missile
            kml_utils.create_kml_point(
                kml_folder=kml_folder,
                lat_deg=position_dict[self.latdeg_colname],
                lon_deg=position_dict[self.londeg_colname],
                alt_meters=position_dict[self.altm_colname],
                style=simplekml.Style(), #TODO
#                    pnt_label=f'Time: {position_dict[self.time_col_name]}',
                timespan_begin=timespan_begin,
                timespan_end=pnt_timespan_end,
            )
            # Add linestring indicating trajectory over previous timestep
            if idx != self.data.index.min():
                prev_position_dict = self.data.loc[idx-1].to_dict()       
                kml_utils.create_kml_linestring(
                    kml_folder=kml_folder,
                    lon_lat_alt_list=[
                        (prev_position_dict[self.londeg_colname],
                         prev_position_dict[self.latdeg_colname],
                         prev_position_dict[self.altm_colname]
                         ),
                        (position_dict[self.londeg_colname],
                         position_dict[self.latdeg_colname],
                         position_dict[self.altm_colname]
                         ),
                    ],
                    style=simplekml.Style(), #TODO
                    label='',
                    timespan_begin=timespan_begin,
                    timespan_end='',
                    close_linestring=False,
                )


if __name__ == '__main__':
    kml_test = KMLTrajectory(data=data)
    kml_test.create_trajectory()
    kml_test.kml.savekmz('test.kml')
