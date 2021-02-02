import numpy as np


def exclude_y_value_when_error_is_nan(axis, error_axis):
    axis_cleaned = []
    error_axis_cleaned = []

    for _x, _error in zip(axis, error_axis):
        if (_x == "None") or (_error == "None") or (_x is None) or (_error is None):
            axis_cleaned.append(np.NaN)
            error_axis_cleaned.append(np.NaN)
        else:
            axis_cleaned.append(np.float(_x))
            error_axis_cleaned.append(np.float(_error))

    return axis_cleaned, error_axis_cleaned


def check_size(x_axis=None, y_axis=None):
    size_x = len(x_axis)
    size_y = len(y_axis)
    min_len = np.min([size_x, size_y])
    return x_axis[:min_len], y_axis[:min_len]


def get_n_random_int_of_max_value_m(n=1, max=10):
    list_random = np.random.random(n) * max
    list_random_int = [np.int(_value) for _value in list_random]
    return list_random_int


def reject_outliers(array=None):
    if len(array) < 3:
        return array

    new_array = [_value
                 for _value in array
                 if (not (_value == np.min(array)))
                 and (not (_value == np.max(array)))]
    return new_array


def reject_n_outliers(array=None, n=1):
    set_array = list(array)
    set_array.sort()
    return set_array[n: -n]


def find_nearest_index(array, value):
    idx = (np.abs(np.array(array) - value)).argmin()
    return idx


def get_closest_index(array=None, value=None):
    idx = (np.abs(np.array(array) - value)).argmin()
    return idx


def get_nearest_index(array=None, value=None):
    return get_closest_index(array=array, value=value)
