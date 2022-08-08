import numpy as np


def get_distance_between_two_points(from_x=None, from_y=None, to_x=None, to_y=None):
    if (from_x is None) or (from_y is None) or (to_x is None) or (to_y is None):
        raise ValueError("Provide from_x, from_y, to_x and to_y values!")

    distance = np.sqrt(np.power(from_y - to_y, 2) + np.power(from_x - to_x, 2))
    return distance


def mean_square_error(imageA, imageB):
    """https://www.pyimagesearch.com/2014/09/15/python-compare-two-images/

    The mean square error between the two images is the sum of the squared difference between the two images:
    Note: the two images must have the same dimension
    """
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])t

    return err
