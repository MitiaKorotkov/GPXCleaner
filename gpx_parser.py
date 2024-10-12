from typing import List
import xml.etree.ElementTree as et
from os.path import dirname
from os import makedirs
import csv
from numpy import pi as PI
from pandas import to_datetime


GPX_NAMESPACE = {"gpx": "http://www.topografix.com/GPX/1/1"}
TRACK_FILES_DIRECTORY = "tracks"
TMP_FILES_DIRECTORY = "tmps"


def make_relevant_name(filename: str) -> str:
    correct_name = []
    for ch in filename:
        if ch.isalpha() or ch.isdigit():
            correct_name.append(ch)
    return "".join(correct_name).lower()


def write_waypoints_to_csv(
    waypoints: et.Element,
    track_name: str,
    file_to_write: (str | None) = None,
    add: bool = True,
) -> None:
    """_summary_

    Args:
        waypoints (et.Element): _description_
        track_name (str): _description_
        file_to_write (str  |  None, optional): _description_. Defaults to None.
        add (bool, optional): _description_. Defaults to True.
    """
    filename = (
        f"./{TMP_FILES_DIRECTORY}/{file_to_write}"
        if file_to_write
        else f"./{TMP_FILES_DIRECTORY}/wpts_{track_name}"
    )
    if not add:
        makedirs(dirname(filename), exist_ok=True)
        with open(f"{filename}.csv", "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file, dialect="excel")
            writer.writerows([["lat", "lon", "name"]])

    with open(f"{filename}.csv", "a", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file, dialect="excel")

        for waypoint in waypoints:
            name = waypoint.findtext(
                "./gpx:name", default="ПУСТО", namespaces=GPX_NAMESPACE
            )

            lattitude = float(waypoint.attrib["lat"]) * PI / 180
            longitude = float(waypoint.attrib["lon"]) * PI / 180

            writer.writerows([[lattitude, longitude, name]])


def write_trkseg_to_csv(
    track_segment: et.Element,
    track_name: str,
    file_to_write: (str | None) = None,
    add: bool = True,
) -> None:
    """This function take one segment of track and create csv file with
    information about its points. Each point represented by a raw containing
    lattitude, longitude, elevation, day and time in this order.

    Args:
        track_segment (et.Element): element tree with part of track you want process
        track_name (str): name of track
        file_to_write (str  |  None, optional): if you want to write to your own
        file name format you can cpecified it. Defaults to None.
        add (bool, optional): if its True file will be aded to the end of already exists
        one. Defaults to True.
    """
    filename = (
        f"./{TMP_FILES_DIRECTORY}/{file_to_write}"
        if file_to_write
        else f"./{TMP_FILES_DIRECTORY}/track_{track_name}"
    )

    if not add:
        makedirs(dirname(filename), exist_ok=True)
        with open(f"{filename}.csv", "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file, dialect="excel")
            writer.writerows([["lat", "lon", "ele", "date"]])

    with open(f"{filename}.csv", "a", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file, dialect="excel")

        points = track_segment.findall("./gpx:trkpt", namespaces=GPX_NAMESPACE)

        for point in points:
            lattitude = float(point.attrib["lat"]) * PI / 180
            longitude = float(point.attrib["lon"]) * PI / 180

            elevation = point.findtext("./gpx:ele", default=0, namespaces=GPX_NAMESPACE)
            elevation = round(float(elevation), 1)

            data = point.findtext("./gpx:time", namespaces=GPX_NAMESPACE)[:-1].split(
                "T"
            )
            datetime = to_datetime(' '.join(data))

            writer.writerows([[lattitude, longitude, elevation, datetime]])


def gpx_to_csv(trip_name: str, track_filenames: List[str]) -> None:
    """This function read gpx file and write different segments of track in
    different csv files. Each track point in csv represented by a raw containing
    lattitude, longitude, elevation, day and time in this order.

    Args:
        trip_name (str): name of directory with .gpx files
        track_filenames (List[str]): name of .gpx files without resolution
    """
    track_file_exists = False
    wpts_file_exists = False
    track_name = ""
    for track_filename in track_filenames:
        root = et.parse(
            f"./{TRACK_FILES_DIRECTORY}/{trip_name}/{track_filename}.gpx"
        ).getroot()

        if not track_file_exists:
            track_name = root.find("./gpx:trk/gpx:name", namespaces=GPX_NAMESPACE).text
            track_name = make_relevant_name(track_name)
        track = root.findall(".//gpx:trkseg", namespaces=GPX_NAMESPACE)
        waypoints = root.findall(".//gpx:wpt", namespaces=GPX_NAMESPACE)

        for segment in track:
            write_trkseg_to_csv(segment, track_name, add=track_file_exists)
            track_file_exists = True

        write_waypoints_to_csv(waypoints, track_name, add=wpts_file_exists)
        wpts_file_exists = True
