import xml.etree.ElementTree as ET
from os.path import dirname
from os import makedirs
import csv
from numpy import pi


TRACK_FILENAME = "Bezengi.gpx"
GPX_NAMESPACE = {"gpx": "http://www.topografix.com/GPX/1/1"}

TRACK_FILES_DIRECTORY = "./tracks/"
TMP_FILES_DIRECTORY = "./tmps/"


def waypoints_to_csv(
    waypoints: ET.Element,
    track_name: str,
    csv_filename: str = None,
) -> None:
    parsed_points = [["lat", "lon", "name"]]
    for i, waypoint in enumerate(waypoints):
        name = waypoint.findtext("./gpx:name", default='ПУСТО', namespaces=GPX_NAMESPACE)
        
        lattitude = float(waypoint.attrib["lat"]) * pi / 180
        longitude = float(waypoint.attrib["lon"]) * pi / 180

        parsed_points.append([lattitude, longitude, name])
    
    filename = (
        f"{TMP_FILES_DIRECTORY}{csv_filename}"
        if csv_filename
        else f"{TMP_FILES_DIRECTORY}{track_name}_wpts"
    )
    makedirs(dirname(filename), exist_ok=True)
    with open(f"{filename}.csv", "w", newline="", encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, dialect="excel")
        writer.writerows(parsed_points)

    return None

def write_trkseg_to_csv(
    track_segment: ET.Element,
    track_name: str,
    segment_name: str,
    csv_filename: str = None,
) -> None:
    """This function take one segment of track and create csv file with
    information about its points. Each point represented by a raw containing
    lattitude, longitude, elevation, day and time in this order.
    """
    points = track_segment.findall("./gpx:trkpt", namespaces=GPX_NAMESPACE)

    parsed_points = [["lat", "lon", "ele", "day", "time"]]
    for point in points:
        lattitude = float(point.attrib["lat"]) * pi / 180
        longitude = float(point.attrib["lon"]) * pi / 180

        elevation = point.findtext("./gpx:ele", default=0, namespaces=GPX_NAMESPACE)
        elevation = round(float(elevation), 1)

        data = point.findtext("./gpx:time", namespaces=GPX_NAMESPACE)[:-1].split("T")
        day = data[0]
        time = data[1]

        parsed_points.append([lattitude, longitude, elevation, day, time])

    filename = (
        f"{TMP_FILES_DIRECTORY}{csv_filename}"
        if csv_filename
        else f"{TMP_FILES_DIRECTORY}{track_name}_{segment_name}"
    )
    makedirs(dirname(filename), exist_ok=True)
    with open(f"{filename}.csv", "w", newline="", encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, dialect="excel")
        writer.writerows(parsed_points)

    return None


def gpx_to_csv(track_filename: str) -> None:
    """This function read gpx file and write different segments of track in
    different csv files. Each track point in csv represented by a raw containing
    lattitude, longitude, elevation, day and time in this order.

    Args:
        track_filename (str): name of gpx file with track
    """
    root = ET.parse(f"{TRACK_FILES_DIRECTORY}{track_filename}").getroot()
    track_name = root.find("./gpx:trk/gpx:name", namespaces=GPX_NAMESPACE).text
    track = root.findall(".//gpx:trkseg", namespaces=GPX_NAMESPACE)
    waypoints = root.findall(".//gpx:wpt", namespaces=GPX_NAMESPACE)

    for i, segment in enumerate(track):
        write_trkseg_to_csv(segment, track_name, i)

    waypoints_to_csv(waypoints, track_name)
    
    return None


gpx_to_csv(TRACK_FILENAME)
