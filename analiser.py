import numpy as np
import pandas as pd

import plotly.graph_objs as go

from spheric_geometry import arc_distance, angle_between_segments, spheric_to_decart


CSV_TRACK_FILENAME = "./tmps/Орехово-Зуевский район Поход_0.csv"
ORIENT_MODE = 1

# Unpack csv
points_df = pd.read_csv(CSV_TRACK_FILENAME)
lons = np.array(points_df["lon"])
lats = np.array(points_df["lat"])

points = np.array(list(zip(lats, lons)))
decart_coords = np.array([spheric_to_decart(np.pi / 2 - p[1], p[0]) for p in points])
vectorized_segments = decart_coords[1:] - decart_coords[:-1]

#shperic metrics
angles = np.array(
    [angle_between_segments(*points[i : i + 3]) for i in range(len(points) - 2)]
)
arc_lengths = np.array([arc_distance(*points[i : i + 2]) for i in range(len(points) - 1)])
distances_from_begin = np.cumsum(arc_lengths)

#oriented angles
vec1 = np.cross(*vectorized_segments[0: 2])
orientations = np.array([np.sign(np.cross(*vectorized_segments[i: i + 2]) @ vec1) for i in range(len(vectorized_segments) - 1)])
oriented_angles = (np.pi - angles.T) * orientations

#distances from start point
dist_from_start = np.array([arc_distance(points[0], points[i]) for i in range(len(points))])
diriv = np.array([(dist_from_start[i] - dist_from_start[i + 1]) for i in range(len(dist_from_start) - 1)])

# Plot
num_steps = 100
param = angles
trace_list = [
    go.Scatter(visible=True, x=distances_from_begin, y=param, mode="lines+markers", name="angles")
]

for N in range(1, 300, 3):
    # Sums of params between N neighboring segments
    sums = np.array([sum(param[i : i + N]) / N for i in range(len(param) - N)])
    # sums = np.array([arc_distance(points[i], points[i + N]) for i in range(len(points) - N)])
    
    trace_list.append(
        go.Scatter(
            visible=False,
            x=distances_from_begin[0:-N],
            y=sums,
            mode="lines+markers",
            name="angles",
        )
    )

fig = go.Figure(data=trace_list)

steps = []
for i in range(num_steps):
    step = dict(method="restyle", args=["visible", [False] * len(fig.data)])
    step["args"][1][i] = True

    steps.append(step)

sliders = [dict(steps=steps)]
fig.layout.sliders = sliders

fig.show()