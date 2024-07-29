import numpy as np


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


def spheric_to_decart(theta, phi, r=EARTH_RADIUS):
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)
    return x, y, z
