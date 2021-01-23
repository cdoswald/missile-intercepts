"""Utility functions for creating Keyhole Markup Language (KML) files."""

# Import packages
from typing import List, Tuple

import pykml
import simplekml

# Define functions
def create_kml_pnt_style(
    icon_path: str,
    icon_scale: float = 1.0,
) -> simplekml.styleselector.Style:
    """Create a simplekml Style object with specified icon and scale."""
    style = simplekml.Style()
    style.iconstyle.icon.href = icon_path
    style.iconstyle.scale = icon_scale
    return style

def create_kml_point(
    kml_folder: simplekml.featgeom.Folder,
    lat_deg: float,
    lon_deg: float,
    style: simplekml.styleselector.Style,
    alt_meters: float = 0,
    pnt_label: str = '',
    timespan_begin: str = '',
    timespan_end: str = '',
) -> simplekml.featgeom.Folder:
    """Create a simplekml Point object with location, time, and style attributes."""
    pnt = kml_folder.newpoint(name=pnt_label, coords=[(lon_deg, lat_deg, alt_meters)])
    pnt.altitudemode = simplekml.AltitudeMode.relativetoground
    pnt.style = style
    pnt.timespan.begin = timespan_begin
    pnt.timespan.end = timespan_end
    return kml_folder

def create_kml_linestring(
    kml_folder: simplekml.featgeom.Folder,
    lon_lat_alt_list: List[Tuple[float, float, float]], #Longitude, latitude, altitude for simplekml
    style: simplekml.styleselector.Style,
    label: str = '',
    close_linestring: bool = False,
    timespan_begin: str = '',
    timespan_end: str = '',
) -> simplekml.featgeom.Folder:
    """Create a simplekml Linestring object with location and style attributes."""
    linestring = kml_folder.newlinestring(name=label)
    if close_linestring:
        lon_lat_alt_list.append(lon_lat_alt_list[0])
    linestring.coords = lon_lat_alt_list
    linestring.altitudemode = simplekml.AltitudeMode.relativetoground
    linestring.style = style
    linestring.timespan.begin = timespan_begin
    linestring.timespan.end = timespan_end
    return kml_folder

def create_kml_polygon():
    """Placeholder for simplekml polygon function."""
    pass

def create_kml_camera():
    """Placeholder for simplekml camera function."""
    pass
