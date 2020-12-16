import numpy as np


def get_distance_between_two_points(from_x=None, from_y=None, to_x=None, to_y=None):
    if (from_x is None) or (from_y is None) or (to_x is None) or (to_y is None):
        raise ValueError("Provide from_x, from_y, to_x and to_y values!")

    distance = np.sqrt(np.power(from_y - to_y, 2) + np.power(from_x - to_x, 2))
    return distance
