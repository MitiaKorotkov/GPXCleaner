import xml.etree.ElementTree as ET
import csv
import typing


TRACK_FILENAME = "gvan.gpx"
GPX_NAMESPACE = {"gpx": "http://www.topografix.com/GPX/1/1"}


class GeoPoint:
    def __init__(self):
        self.lat
        self.lon
        self.ele
        self.time

    def __repr__(self) -> str:
        pass


def gpx_to_csv(track_filename: str = TRACK_FILENAME) -> None:
    """_summary_

    Returns:
        _type_: _description_
    """
    root = ET.parse(track_filename).getroot()
    track_name = root.find("./gpx:trk/gpx:name", namespaces=GPX_NAMESPACE).text
    track = root.findall(".//gpx:trkseg", namespaces=GPX_NAMESPACE)

    for i, segment in enumerate(track):
        points = segment.findall("./gpx:trkpt", namespaces=GPX_NAMESPACE)

        parsed_points = []
        for point in points:
            lattitude = point.attrib["lat"]
            longitude = point.attrib["lon"]

            elevation = point.findtext("./gpx:ele", default=0, namespaces=GPX_NAMESPACE)
            elevation = round(float(elevation), 1)

            data = point.findtext("./gpx:time", namespaces=GPX_NAMESPACE)[:-1].split("T")
            day = data[0]
            time = data[1]

            parsed_points.append([lattitude, longitude, elevation, day, time])

        with open(f"{track_name}_part_{i}.csv", "w", newline="") as csv_file:
            writer = csv.writer(csv_file, dialect="excel")
            writer.writerows(parsed_points)

    return None


gpx_to_csv()
