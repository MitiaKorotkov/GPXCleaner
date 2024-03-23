track_filename = "gvan.gpx"

with open(track_filename, encoding="utf-8") as track_file:
    data = track_file.read()

print(data)