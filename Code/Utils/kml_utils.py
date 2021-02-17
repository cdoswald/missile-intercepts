"""Utility functions for creating Keyhole Markup Language (KML) files."""
#TODO: add stylemaps to all style functions

# Import packages
import os
from typing import List, Optional, Tuple

import numpy as np

import simplekml

# Import local modules
#script_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
#sys.path.insert(0, script_dir)
import geo_utils as geo

# Define functions
def save_kmz(
    kml: simplekml.kml.Kml,
    output_dir: str,
    output_file_name: str,
    attachment_dir: Optional[str] = None,
    attachment_files_list: Optional[List[str]] = None,
    attachment_suffix_list: Optional[List[str]] = None,
) -> None:
    """Save simplekml KML with attachments in zipped .kmz file format. If 
    attachment directory is provided, a list of attachment file names or 
    suffixes must also be provided to include the attachments in the .kmz file.
    """
    if attachment_dir is not None and attachment_files_list:
        for file in attachment_files_list:
            kml.addfile(os.path.join(attachment_dir, file))
    elif attachment_dir is not None and attachment_suffix_list:
        for file in os.listdir(attachment_dir):
            file_suffix = file.split('.', expand=True)[-1]
            if file_suffix in attachment_suffix_list:
                kml.addfile(os.path.join(attachment_dir, file))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    kml.savekmz(os.path.join(output_dir, f'{output_file_name}.kmz'))
    
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

def create_kml_linestring_style(
    color: str,
    width: float = 1,
) -> simplekml.styleselector.Style:
    """Create a simplekml linestring Style object with specified color and width."""
    style = simplekml.Style()
    style.linestyle.color = color
    style.linestyle.width = width
    return style

def create_kml_track_style( 
    icon_path: str,
    linestring_color: str,
    icon_scale: float = 1.0,
    linestring_width: float = 1.0,
) -> simplekml.styleselector.Style:
    """Create a simplekml GxTrack Style object with specified icon and linestring."""
    style = simplekml.Style()
    style.iconstyle.icon.href = icon_path
    style.iconstyle.scale = icon_scale
    style.linestyle.color = linestring_color
    style.linestyle.width = linestring_width
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

def add_kml_circle_linestring(
    kml_folder: simplekml.featgeom.Folder,
    origin_lat_deg: float,
    origin_lon_deg: float,
    radius_km: float,
    style: simplekml.styleselector.Style,
    linestring_label: str = '',
    timespan_begin: str = '',
    timespan_end: str = '',
) -> simplekml.featgeom.Folder:
    """Add a simplekml circular Linestring object to existing KML folder.
    
    Arguments
        kml_folder: simplekml folder to which to add a new linestring object
        origin_lat_deg: latitude of center point in degrees
        origin_lon_deg: longitude of center point in degrees
        radius_km: distance from origin to all points on linestring in kilometers
        style: simplekml linestring style
        linestring_label: string label for linestring
        timespan_begin: string (in KML format) indicating linestring start time
        timespan_end: string (in KML format) indicating linestring end time

    Returns
        kml_folder: simplekml folder with newly added linestring object
    """
    linestring = kml_folder.newlinestring(name=linestring_label)
    coords_list = []
    for angle_deg in np.arange(361):
        latlon_deg = geo.determine_destination_coords(
            origin_lat_deg=origin_lat_deg,
            origin_lon_deg=origin_lon_deg,
            distance_km=radius_km,
            angle_deg=angle_deg,
        )
        coords_list.append(
            (latlon_deg[1], latlon_deg[0]) # Longitude first for simplekml
        ) 
    linestring.coords = coords_list
    linestring.style = style
    linestring.timespan.begin = timespan_begin
    linestring.timespan.end = timespan_end
    linestring.altitudemode = simplekml.AltitudeMode.relativetoground
    return kml_folder
    #TODO: streamline by calling add_kml_linestring with specific args

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
    collada_model_link: str,
    alt_meters: float = 0,
    heading_deg: float = 0,
    tilt_deg: float = 0,
    roll_deg: float = 0,
    x_scale: float = 1,
    y_scale: float = 1,
    z_scale: float = 1,
    model_label: str = '',
    timespan_begin: str = '',
    timespan_end: str = '',
) -> simplekml.featgeom.Folder:
    """Add a simplekml Model object to existing KML folder.
    
    Arguments
        kml_folder: simplekml folder to which to add a new Model object
        lat_deg: point latitude in degrees
        lon_deg: point longitude in degrees
        collada_model_link: path or URL to COLLADA file (.dae) containing model
        alt_meters: point altitude in meters (relative to ground)
        heading_deg: rotation about the z-axis
        tilt_deg: rotation about the x-axis (parallel to latitude lines)
        roll_deg: rotation about the y-axis (parallel to longitude lines)
        x_scale: scale of the model along the x axis
        y_scale: scale of the model along the y axis
        z_scale: scale of the model along the z axis
        model_label: string label for model
        timespan_begin: string (in KML format) indicating model start time
        timespan_end: string (in KML format) indicating model end time

    Returns
        kml_folder: simplekml folder with newly added Model object
    """
    model = kml_folder.newmodel(name=model_label)
    model.location = simplekml.Location(lon_deg, lat_deg, alt_meters)
    model.orientation = simplekml.Orientation(heading_deg, tilt_deg, roll_deg)
    model.scale = simplekml.Scale(x_scale, y_scale, z_scale)
    model.link = simplekml.Link(href=collada_model_link)
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
