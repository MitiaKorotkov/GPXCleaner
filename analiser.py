import plotly.graph_objs as go

import numpy as np
import pandas as pd


CSV_TRACK_FILENAME = "./tmps/Трек_0.csv"
EARTH_RADIUS = 6371 * 10e2


def hav(point_1, point_2):
    """_summary_

    Args:
        point_1 (_type_): _description_
        point_2 (_type_): _description_

    Returns:
        _type_: _description_
    """
    phi_1, lambda_1 = point_1
    phi_2, lambda_2 = point_2

    return np.sin((phi_2 - phi_1) / 2) ** 2 + np.cos(phi_1) * np.cos(phi_2) * (
        np.sin((lambda_2 - lambda_1) / 2) ** 2
    )


def arc_distance(point_1, point_2):
    """_summary_

    Args:
        point_1 (_type_): _description_
        point_2 (_type_): _description_

    Returns:
        _type_: _description_
    """
    h = hav(point_1, point_2)
    return 2 * EARTH_RADIUS * np.arcsin(np.sqrt(h))


def angle_between_segments(point_A, point_B, point_C):
    """_summary_

    Args:
        point_A (_type_): _description_
        point_B (_type_): _description_
        point_C (_type_): _description_

    Returns:
        _type_: _description_
    """
    cos_a = 1 - 2 * hav(point_B, point_C)
    cos_b = 1 - 2 * hav(point_A, point_C)
    cos_c = 1 - 2 * hav(point_A, point_B)

    sin_a = np.sqrt(1 - cos_a**2)
    sin_c = np.sqrt(1 - cos_c**2)

    B = (cos_b - cos_a * cos_c) / sin_a / sin_c

    return np.arccos(B) if (B < 1 and B > -1) else np.pi


# Unpack csv and calculate angles between neighboring segments
points_df = pd.read_csv(CSV_TRACK_FILENAME)

lons = np.array(points_df["lon"])
lats = np.array(points_df["lat"])

points = np.array(list(zip(lats, lons)))
angles = np.array(
    [angle_between_segments(*points[i : i + 3]) for i in range(len(points) - 2)]
)
distances = np.cumsum(
    [arc_distance(*points[i : i + 2]) for i in range(len(points) - 1)]
)

# Plot
num_steps = 100
trace_list = [
    go.Scatter(visible=True, x=distances, y=angles, mode="lines+markers", name="angles")
]

for N in range(1, 300, 3):
    # Sums of angles between N neighboring segments
    sums = np.array([sum(angles[i : i + N]) / N for i in range(len(angles) - N)])

    trace_list.append(
        go.Scatter(
            visible=False,
            x=distances[0:-N],
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
