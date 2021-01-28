"""Utility functions for creating Keyhole Markup Language (KML) files."""

#TODO: add heading, tilt, and roll to GxTrack style
#TODO: add stylemaps to all style functions

# Import packages
from typing import List, Tuple

import pykml
import simplekml

# Define functions
def create_kml_point_style(
    icon_path: str,
    icon_scale: float = 1.0,
    heading: float = 0.0,
) -> simplekml.styleselector.Style:
    """Create a simplekml point Style object with specified icon and scale."""
    style = simplekml.Style()
    style.iconstyle.icon.href = icon_path
    style.iconstyle.scale = icon_scale
    style.iconstyle.heading = heading
    return style

def create_kml_track_style( 
    icon_path: str,
    icon_scale: float = 1.0,
) -> simplekml.styleselector.Style:
    """Create a simplekml GxTrack Style object with specified icon and scale."""
    style = simplekml.Style()
    style.iconstyle.icon.href = icon_path
    style.iconstyle.scale = icon_scale
    style.linestyle.color = simplekml.Color.darkgoldenrod #TODO: add argument
    style.linestyle.width = 6 #TODO: add argument
    return style

def add_kml_point(
    kml_folder: simplekml.featgeom.Folder,
    lat_deg: float,
    lon_deg: float,
    style: simplekml.styleselector.Style,
    alt_meters: float = 0,
    pnt_label: str = '',
    timespan_begin: str = '',
    timespan_end: str = '',
) -> simplekml.featgeom.Folder:
    """Add a simplekml Point object to existing KML folder.
    
    Arguments
        kml_folder: simplekml folder to which to add a new point object
        lat_deg: point latitude in degrees
        lon_deg: point longitude in degrees
        style: simplekml point style
        alt_meters: point altitude in meters (relative to ground)
        pnt_label: string label for point
        timespan_begin: string (in KML format) indicating point start time
        timespan_end: string (in KML format) indicating point end time
    
    Returns
        kml_folder: simplekml folder with newly added point object
    """
    pnt = kml_folder.newpoint(
        name=pnt_label,
        coords=[(lon_deg, lat_deg, alt_meters)]
    )
    pnt.style = style
    pnt.timespan.begin = timespan_begin
    pnt.timespan.end = timespan_end
    pnt.altitudemode = simplekml.AltitudeMode.relativetoground
    return kml_folder

def add_kml_linestring(
    kml_folder: simplekml.featgeom.Folder,
    lon_lat_alt_list: List[Tuple[float, float, float]],
    style: simplekml.styleselector.Style,
    linestring_label: str = '',
    timespan_begin: str = '',
    timespan_end: str = '',
    close_linestring: bool = False,
) -> simplekml.featgeom.Folder:
    """Add a simplekml Linestring object to existing KML folder.
    
    Arguments
        kml_folder: simplekml folder to which to add a new linestring object
        lon_lat_alt_list: list of 3-length tuples indicating longitude (degrees),
            latitude (degrees), and altitude (meters) for each point in linestring;
            NOTE that longitude precedes latitude in simplekml objects
        style: simplekml linestring style
        linestring_label: string label for linestring
        timespan_begin: string (in KML format) indicating linestring start time
        timespan_end: string (in KML format) indicating linestring end time
        close_linestring: flag if linestring should connect from last point
            to first point in lon_lat_alt_list
    
    Returns
        kml_folder: simplekml folder with newly added linestring object
    """
    linestring = kml_folder.newlinestring(name=linestring_label)
    if close_linestring:
        lon_lat_alt_list.append(lon_lat_alt_list[0])
    linestring.coords = lon_lat_alt_list
    linestring.style = style
    linestring.timespan.begin = timespan_begin
    linestring.timespan.end = timespan_end
    linestring.altitudemode = simplekml.AltitudeMode.relativetoground
    return kml_folder

def add_kml_track(
    kml_folder: simplekml.featgeom.Folder,
    lon_lat_alt_list: List[Tuple[float, float, float]],
    timestamp_list: List[str],
    style: simplekml.styleselector.Style,
    track_label: str = '',
) -> simplekml.featgeom.Folder:
    """Add a simplekml GxTrack object to existing KML folder.
    
    Arguments
        kml_folder: simplekml folder to which to add a new GxTrack object
        lon_lat_alt_list: list of 3-length tuples indicating longitude (degrees),
            latitude (degrees), and altitude (meters) for each point in GxTrack;
            NOTE that longitude precedes latitude in simplekml objects
        timestamp_list: list of timestamps (in KML format)
        style: simplekml GxTrack style
        track_label: string label for GxTrack

    Returns
        kml_folder: simplekml folder with newly added GxTrack object
    """
    track = kml_folder.newgxtrack(name=track_label)
    track.newwhen(timestamp_list)
    track.newgxcoord(lon_lat_alt_list)
    track.style = style
    track.altitudemode = simplekml.AltitudeMode.relativetoground
    return kml_folder

def add_kml_model(
    kml_folder: simplekml.featgeom.Folder,
    lat_deg: float,
    lon_deg: float,
    style: simplekml.styleselector.Style,
    alt_meters: float = 0,
    heading_deg: float = 0,
    tilt_deg: float = 0,
    roll_deg: float = 0,
    model_label: str = '',
    timespan_begin: str = '',
    timespan_end: str = '',
) -> simplekml.featgeom.Folder:
    """Add a simplekml Model object to existing KML folder.
    
    Arguments
        kml_folder: simplekml folder to which to add a new Model object
        lat_deg: point latitude in degrees
        lon_deg: point longitude in degrees
        style: simplekml point style
        alt_meters: point altitude in meters (relative to ground)
        heading_deg: rotation about the z-axis
        tilt_deg: rotation about the x-axis
        roll_deg: rotation about the y-axis
        model_label: string label for model
        timespan_begin: string (in KML format) indicating model start time
        timespan_end: string (in KML format) indicating model end time

    Returns
        kml_folder: simplekml folder with newly added Model object
    """
    model = kml_folder.newmodel(name=model_label)
    model.location = simplekml.Location(lon_deg, lat_deg, alt_meters)
    model.orientation = simplekml.Orientation(heading_deg, tilt_deg, roll_deg)
    model.style = style
    model.timespan.begin = timespan_begin
    model.timespan.end = timespan_end
    model.altitudemode = simplekml.AltitudeMode.relativetoground
    return kml_folder


def create_kml_polygon():
    """Placeholder for simplekml polygon function."""
    pass

def create_kml_camera():
    """Placeholder for simplekml camera function."""
    pass
