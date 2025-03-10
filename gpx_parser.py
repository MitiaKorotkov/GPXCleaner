import pandas as pd
import numpy as np

import csv
from os import makedirs, remove
from os.path import dirname

import xml.etree.ElementTree as et

from typing import Generator, List

PI = np.pi

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
            datetime = pd.to_datetime(" ".join(data))

            writer.writerows([[lattitude, longitude, elevation, datetime]])


def gpx_to_csv(dir_name: str, track_filenames: List[str], parse_waypoints=False) -> Generator[str, str, str]:
    """This function read gpx file and write different segments of track in
    different csv files. Each track point in csv represented by a raw containing
    lattitude, longitude, elevation, day and time in this order.

    Args:
        dir_name (str): name of directory with .gpx files
        track_filenames (List[str]): name of .gpx files without resolution
        parse_waypoints (bool, optional): _description_. Defaults to False.

    Returns:
        str: _description_
    """
    track_file_exists = False
    wpts_file_exists = False
    track_name = ""
    for track_filename in track_filenames:
        root = et.parse(
            f"./{TRACK_FILES_DIRECTORY}/{dir_name}/{track_filename}.gpx"
        ).getroot()  # TODO(Dima): Add the ability to open tracks from any directories!

        if not track_file_exists:
            track_name = root.find("./gpx:trk/gpx:name", namespaces=GPX_NAMESPACE).text
            track_name = make_relevant_name(track_name)
        track = root.findall(".//gpx:trkseg", namespaces=GPX_NAMESPACE)
        waypoints = root.findall(".//gpx:wpt", namespaces=GPX_NAMESPACE)

        for segment in track:
            write_trkseg_to_csv(segment, track_name, add=track_file_exists)
            track_file_exists = True

        if parse_waypoints:
            write_waypoints_to_csv(waypoints, track_name, add=wpts_file_exists)
            wpts_file_exists = True

        yield track_name


def read_gpx(dir_name: str, track_filenames: List[str]) -> pd.DataFrame:
    """_summary_

    Args:
        dir_name (str): _description_
        track_filenames (List[str]): _description_

    Returns:
        _type_: _description_
    """
    # TODO(Dima): Add the ability to open tracks from any directories!
    # TODO(Dima): Create tmp directory for csv files here
    df = pd.concat(
        [
            pd.read_csv(f"./{TMP_FILES_DIRECTORY}/track_{segment_name}.csv")
            for segment_name in gpx_to_csv(dir_name, track_filenames)
        ]
    )
    df = df.set_index(np.arange(df.shape[0]))

    start_day = pd.to_datetime(df["date"][0])
    rel_times = pd.to_datetime(df["date"]) - start_day
    df["sec_from_start"] = rel_times / np.timedelta64(1, "s")

    # TODO(Dima): Remove hole tmp directory
    # remove(csv_filename)

    return df

def make_train_pool(dir_name: str, clean_dir_name: str, track_filenames: List[str]) -> pd.DataFrame:
    """
        Читает исходный и очищенный трек в dataframe, добавляет колонку Target 1 - для почищенных точек, 0 - для остальных
    """

    df = read_gpx(dir_name, track_filenames)
    columns = list(df.columns)
    df['lat_norm'] = (df['lat']*1e6).astype(int) 
    df['lon_norm'] = (df['lon']*1e6).astype(int) 
    df['Target_all'] = 1

    clean_df = read_gpx(clean_dir_name, track_filenames)
    clean_df['Target_clean'] = 0
    clean_df['lat_norm'] = (clean_df['lat']*1e6).astype(int) 
    clean_df['lon_norm'] = (clean_df['lon']*1e6).astype(int) 

    groups = clean_df.groupby(["lat_norm", "lon_norm"])[["Target_clean"]]
    clean_df = groups.first()


    result_df = df.merge(clean_df, 'left', suffixes=["", "_clean"], on=["lat_norm", "lon_norm"])

    result_df['Target'] = np.nan_to_num(result_df['Target_clean'], nan=1)
    return result_df[columns + ['Target']]


def write_to_gpx(df: pd.DataFrame, filename: str) -> None:
    coordinates = [
        (lat / np.pi * 180, lon / np.pi * 180, time)
        for lat, lon, time in zip(df["lat"], df["lon"], df["date"])
    ]

    gpx = et.Element("gpx", version="1.1", xmlns="http://www.topografix.com/GPX/1/1")

    track = et.SubElement(gpx, "trk")
    name = et.SubElement(gpx, "name")
    track_name = et.SubElement(track, "name")
    track_segment = et.SubElement(track, "trkseg")

    name.text = "tmp_name"
    track_name.text = "tmp_name"

    for lat, lon, t in coordinates:
        point = et.SubElement(
            track_segment, "trkpt", attrib={"lat": str(lat), "lon": str(lon)}
        )
        point_time = et.SubElement(point, "time")
        point_time.text = t

    tree = et.ElementTree(gpx)

    tree.write(filename, encoding="utf-8", xml_declaration=True)
