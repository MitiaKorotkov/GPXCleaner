import numpy as np
from sklearn.cluster import DBSCAN
from metrics import (
    add_arc_distances_from_start,
    add_lengths_betwen_segments,
    add_angles_betwen_segments
)


def clean_df_target(df, target_column='Target', window=1):
    '''
        Сначала определяем сколько в текущем отрезке мусорных точек, затем удаляем отрезки длины <= window

    '''
    cur_dist = 0
    dists = []
    for el in df[target_column]:
        if el == 1:
            cur_dist += 1
        else:
            cur_dist = 0
        dists.append(cur_dist)
    for i in range(len(dists) - 2, 0, -1):
        if dists[i + 1] > 0 and dists[i] > 0:
            dists[i] = dists[i + 1]
    
    df[target_column] = np.where(np.array(dists) > window, 1, 0)



def add_features(df):
    add_arc_distances_from_start(df)
    add_angles_betwen_segments(df)
    add_lengths_betwen_segments(df)

    epsilon = df["lengths_betwen_segments"].mean() / 3

    points = np.array(list(zip(df["lat"], df["lon"])))
    db = DBSCAN(eps=epsilon, min_samples=2).fit(points)

    labels = db.labels_
    df['dbscan_result'] = np.where(labels == -1, 0, 1)

    ns_rolling_window = [n for n in range(5, 100, 10)] # Размеры скользящего окна

    for n in ns_rolling_window:
        df[f"angles_betwen_segments_{n}"] = df["angles_betwen_segments"].rolling(window=n, center=True).mean()
    return df