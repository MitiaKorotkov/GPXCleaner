import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

CSV_TRACK_FILENAME = "./tmps/Трек_0"
EARTH_RADIUS = 64 * 10e5


def arc_distance(phi_1, phi_2, lambda_1, lambda_2):
    h = np.sin((phi_2 - phi_1) / 2) ** 2 + np.cos(phi_1) * np.cos(phi_2) * (np.sin((lambda_2 - lambda_1) / 2) ** 2)
    return 2 * EARTH_RADIUS * np.arcsin(np.sqrt(h))

points = pd.read_csv(f"{CSV_TRACK_FILENAME}.csv")
print(points["ele"])

lons = np.array(points["lon"])
lats = np.array(points["lat"])

print(lons)
print(lats)

plt.scatter(lons, lats)
plt.show()