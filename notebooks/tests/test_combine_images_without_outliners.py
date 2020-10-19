from notebooks.__code.combine_images_without_outliers.combine_images import CombineImagesAlgorithm
import pytest
import numpy as np


class TestCombineImagesWithOutliners:

    def test_raises_error_when_no_arrays(self):
        with pytest.raises(ValueError):
            CombineImagesAlgorithm()

    def test_raises_error_if_less_than_3_arrays(self):
        list_array = [np.arange(10), np.arange(10)]
        with pytest.raises(ValueError):
            CombineImagesAlgorithm(list_array=list_array)

    def test_make_sure_arrays_have_the_same_size(self):
        list_array = [np.arange(10), np.arange(9), np.arange(9)]
        with pytest.raises(ValueError):
            CombineImagesAlgorithm.check_arrays_have_same_size_and_dimensions(list_array=list_array)

    def test_make_sure_arrays_have_the_same_dimensions(self):
        list_array = [np.array([[1, 2, 3], [1, 2, 3]]),
                      np.array([[1, 2, 3], [1, 2, 3]]),
                      np.array([[1, 2, 3], [1, 2]])]
        with pytest.raises(ValueError):
            CombineImagesAlgorithm.check_arrays_have_same_size_and_dimensions(list_array=list_array)

    def test_mean_without_outliers_3_arrays(self):
        array1 = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        array2 = np.array([[5, 5, 5], [5, 5, 5], [5, 5, 5]])
        array3 = np.array([[10, 2, 5], [10, 10, 10], [3, 3, 3]])
        mean_array_calculated = CombineImagesAlgorithm.mean_without_outliers(list_array=[array1, array2, array3])
        mean_array_expected = np.array([[5, 2, 5], [5, 5, 6], [5, 5, 5]])
        [nbr_row, nbr_col] = np.shape(mean_array_expected)
        for _row in np.arange(nbr_row):
            for _col in np.arange(nbr_col):
                _counts_expected = mean_array_expected[_row, _col]
                _count_calculated = mean_array_calculated[_row, _col]
                assert _counts_expected == _count_calculated

    def test_mean_without_outliers_4_arrays(self):
        array1 = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        array2 = np.array([[5, 5, 5], [5, 5, 5], [5, 5, 5]])
        array3 = np.array([[20, 0, 0], [6, 6, 1], [1, 1, 20]])
        array4 = np.array([[10, 2, 5], [10, 10, 10], [3, 3, 3]])
        mean_array_calculated = CombineImagesAlgorithm.mean_without_outliers(
            list_array=[array1, array2, array3, array4])
        mean_array_expected = np.array([[7.5, 2, 4], [5.5, 5.5, 5.5], [4, 4, 7]])
        [nbr_row, nbr_col] = np.shape(mean_array_expected)
        for _row in np.arange(nbr_row):
            for _col in np.arange(nbr_col):
                _counts_expected = mean_array_expected[_row, _col]
                _count_calculated = mean_array_calculated[_row, _col]
                assert _counts_expected == _count_calculated
