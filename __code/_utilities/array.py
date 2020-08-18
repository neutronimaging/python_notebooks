import copy
import numpy as np


def exclude_y_value_when_error_is_nan(axis, error_axis):
	axis_cleaned = []
	error_axis_cleaned = []

	for _x, _error in zip(axis, error_axis):
		if (_x is None) or (_error is None):
			axis_cleaned.append(np.NaN)
			error_axis_cleaned.append(np.NaN)
		else:
			axis_cleaned.append(_x)
			error_axis_cleaned.append(_error)

	return axis_cleaned, error_axis_cleaned
