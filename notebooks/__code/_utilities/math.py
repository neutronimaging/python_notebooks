import numpy as np


def get_distance_between_two_points(from_pixel=None,
                                    to_pixel=None):
    if (from_pixel is None) or (to_pixel is None):
        raise ValueError("Provide a from_pixel and to_pixel dictionaries {'x': value, 'y': value}!")

    from_pixel_x = from_pixel.get('x', np.NaN)
    from_pixel_y = from_pixel.get('y', np.NaN)

    to_pixel_x = to_pixel.get('x', np.NaN)
    to_pixel_y = to_pixel.get('y', np.NaN)

    distance = np.sqrt( np.power(from_pixel_y - to_pixel_y, 2) + np.power(from_pixel_x - to_pixel_x, 2))

    return distance