import plotly.graph_objects as go

import numpy as np
import pandas as pd
from pathlib import Path
import os

from spheric_geometry import arc_distance


def concat_tracks(path):
    days_data = [
        pd.read_csv(file)
        for file in sorted(
            path.glob("*.csv"),
            key=lambda file: int(file.name.split(".")[0].split("_")[-1]),
        )
    ]
    days_data = [data.iloc[::20] for data in days_data]
    
    return pd.concat(
        days_data,
        ignore_index=True,
    )
    
def get_waypoints(path):
    return pd.read_csv(path)

def unpack_points(df):
    lons = np.array(df["lon"])
    lats = np.array(df["lat"])
    
    return np.array(list(zip(lats, lons)))

points_df = concat_tracks(Path("./tmps/"))
waypoints_df = get_waypoints(Path("./tracks/КОЛЬЦО12_wpts.csv"))

points = unpack_points(points_df)
elevations = np.array(points_df["ele"])
waypoints = unpack_points(waypoints_df)

nearest_p = []
for j, waypoint in enumerate(waypoints):
    nearest_p.append(min([[arc_distance(waypoint, p), i] for i, p in enumerate(points)]))
    nearest_p[j][0] = waypoints_df['name'].iloc[j]

arc_lengths = np.array(
    [arc_distance(*points[i : i + 2]) for i in range(len(points) - 1)]
)
distances_from_begin = np.cumsum(arc_lengths)

trace_list = go.Scatter(
    visible=True,
    y=elevations[:-1],
    x=distances_from_begin,
    mode="lines",
    line_shape="spline",
    name="Elevation profile",
    fill="tozeroy",
)
fig = go.Figure(
    data=trace_list,
    layout_yaxis_range=[1300, 4800],
)

for name, i in nearest_p:
    fig.add_vline(
        x=distances_from_begin[i],
        line_width=1,
        line_color="white",
        annotation_text=name,
        # label={
        #     'text': f'\t{name}',
        #     'textposition': "start",
        #     'font': {
        #         'size': 10,
        #         'color': "blue",
        #         },
        #     'yanchor': "middle",
        #     'xanchor': "right",
        # },
        y0=0,
        y1=0.05,
    )
# fig.layout.plot_bgcolor='white'

fig.show()

if not os.path.exists("images"):
    os.mkdir("images")

fig.write_image(f"images/profile.pdf", format='pdf', width=2890, height=1440)