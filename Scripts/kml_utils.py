"""Utility functions for creating Keyhole Markup Language (KML) files."""

# Import packages
from typing import List, Tuple
import numpy as np

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
    fol: simplekml.featgeom.Folder,
    lat: float,
    lon: float,
    style: simplekml.styleselector.Style,
    pnt_label: str = '',
    timespan_begin: str = '',
    timespan_end: str = '',
) -> simplekml.featgeom.Folder:
    """Create a simplekml Point object with location, time, and style attributes."""
    pnt = fol.newpoint(name=pnt_label, coords=[(lon, lat)])
    pnt.style = style
    pnt.timespan.begin = timespan_begin
    pnt.timespan.end = timespan_end
    return fol

def create_kml_linestring(
    fol: simplekml.featgeom.Folder,
    coords_list: List[Tuple[float, float]],
    style: simplekml.styleselector.Style,
    label: str = '',
) -> simplekml.featgeom.Folder:
    """Create a simplekml Linestring object with location and style attributes."""
    linestring = fol.newlinestring(name=label)
    coords_list.append(coords_list[0]) # Close linestring object
    linestring.coords = coords_list
    linestring.style = style
    return fol

def create_kml_polygon():
    """Placeholder for simplekml polygon function."""
    pass

def create_kml_camera():
    """Placeholder for simplekml camera function."""
    pass
