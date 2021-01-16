import pytest
import numpy as np

from __code._utilities import array


def test_reject_outliers():
    my_array = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    expected_array = np.array([2, 3, 4, 5, 6, 7, 8, 9])
    returned_array = array.reject_outliers(array=my_array)
    for _exp, _ret in zip(expected_array, returned_array):
        assert _exp == _ret


def test_reject_n_outliers():
    my_array = np.arange(20)
    n = 5
    expected_array = np.arange(5, 15, 1)
    returned_array = array.reject_n_outliers(array=my_array, n=5)
    returned_array.sort()

    assert len(returned_array) == len(expected_array)
    for _exp, _ret in zip(expected_array, returned_array):
        assert _exp == _ret
