import numpy as np
import pandas as pd

import plotly.graph_objs as go
import matplotlib.pyplot as plt
import seaborn as sns

from spheric_geometry import arc_distance, angle_between_segments, spheric_to_decart


TMP_FILES_DIRECTORY = "tmps"


def create_track_dataframe(track_name: str) -> pd.DataFrame:
    df = pd.read_csv(f"./{TMP_FILES_DIRECTORY}/track_{track_name}.csv")

    start_day = pd.to_datetime(df["date"][0])
    rel_times = pd.to_datetime(df["date"]) - start_day
    df["sec_from_start"] = rel_times / np.timedelta64(1, "s")

    return df


def add_angles_betwen_segments(df: pd.DataFrame) -> None:
    lons = np.array(df["lon"])
    lats = np.array(df["lat"])
    points = np.array(list(zip(lats, lons)))

    angles = np.array(
        [angle_between_segments(*points[i : i + 3]) for i in range(len(points) - 2)]
        + [0, 0]
    )

    df["angles_betwen_segments"] = angles


def add_vector_segments(df: pd.DataFrame) -> None:
    lons = np.array(df["lon"])
    lats = np.array(df["lat"])
    points = np.array(list(zip(lats, lons)))

    decart_coords = [spheric_to_decart(np.pi / 2 - p[1], p[0]) for p in points]
    decart_coords += [decart_coords[-1]]
    decart_coords = np.array(decart_coords)
    print(decart_coords[1:] - decart_coords[:-1])
    # FIXME(Dima): think about correct way to add this to df
    df["vector_segments"] = decart_coords[1:] - decart_coords[:-1]


def add_arc_lengths_betwen_segments(df: pd.DataFrame) -> None:
    lons = np.array(df["lon"])
    lats = np.array(df["lat"])
    points = np.array(list(zip(lats, lons)))

    arc_lengths = np.array(
        [arc_distance(*points[i : i + 2]) for i in range(len(points) - 1)] + [0]
    )

    df["arc_lengths_betwen_segments"] = arc_lengths


def add_arc_distances_from_start(df: pd.DataFrame) -> None:
    lons = np.array(df["lon"])
    lats = np.array(df["lat"])
    points = np.array(list(zip(lats, lons)))

    arc_lengths = np.array(
        [0] + [arc_distance(*points[i : i + 2]) for i in range(len(points) - 1)]
    )

    df["arc_distances_from_start"] = np.cumsum(arc_lengths)


def add_distances_from_start(df: pd.DataFrame) -> None:
    lons = np.array(df["lon"])
    lats = np.array(df["lat"])
    points = np.array(list(zip(lats, lons)))

    decart_coords = np.array(
        [spheric_to_decart(np.pi / 2 - p[1], p[0]) for p in points]
    )
    # TODO(Dima): implement this function
    # df["distances_from_start"] = decart_coords[1:] - decart_coords[:-1]

    """lons = np.array(df["lon"])
    lats = np.array(df["lat"])

    points = np.array(list(zip(lats, lons)))
    decart_coords = np.array([spheric_to_decart(np.pi / 2 - p[1], p[0]) for p in points])
    vectorized_segments = decart_coords[1:] - decart_coords[:-1]
    
    # shperic metrics
    arc_lengths = np.array(
        [arc_distance(*points[i : i + 2]) for i in range(len(points) - 1)]
    )
    distances_from_begin = np.cumsum(arc_lengths)

    # oriented angles
    vec1 = np.cross(*vectorized_segments[0:2])
    orientations = np.array(
        [
            np.sign(np.cross(*vectorized_segments[i : i + 2]) @ vec1)
            for i in range(len(vectorized_segments) - 1)
        ]
    )
    oriented_angles = (np.pi - angles.T) * orientations

    # distances from start point
    dist_from_start = np.array(
        [arc_distance(points[0], points[i]) for i in range(len(points))]
    )
    diriv = np.array(
        [
            (dist_from_start[i] - dist_from_start[i + 1])
            for i in range(len(dist_from_start) - 1)
        ]
    )"""


def add_oriented_angles_betwen_segments(df: pd.DataFrame) -> None:
    # TODO(Dima): implement this function
    pass


def add_velocities(df: pd.DataFrame) -> None:
    # TODO(Dima): implement this function
    pass


def create_wpts_dataframe(track_name: str) -> pd.DataFrame:
    df = pd.read_csv(f"./{TMP_FILES_DIRECTORY}/wpts_{track_name}.csv")
    # TODO(Dima): improve this function
    return df


def make_plot(df: pd.DataFrame, x: str, y: str) -> None:
    # TODO(Dima): implement this function

    # Plot
    num_steps = 100
    grid = df[x]
    param = df[y]
    trace_list = [
        go.Scatter(
            visible=True,
            x=grid,
            y=param,
            mode="lines+markers",
            name=f"{y}({x})",
        )
    ]

    for N in range(1, 300, 3):
        # Sums of params between N neighboring segments
        sums = np.array([sum(param[i : i + N]) / N for i in range(len(param) - N)])
        # sums = np.array([arc_distance(points[i], points[i + N]) for i in range(len(points) - N)])

        trace_list.append(
            go.Scatter(
                visible=False,
                x=grid[0:-N],
                y=sums,
                mode="lines+markers",
                name=f"{y}({x})",
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


def make_pairplt(df: pd.DataFrame) -> None:
    sns.pairplot(df)
    plt.show()