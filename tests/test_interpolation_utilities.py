import pytest
import numpy as np

from __code.interpolation_utilities import Interpolation

EPS = 1e-6


class TestInterpolation:

	def test_minimum_axis_given(self):
		with pytest.raises(ValueError):
			Interpolation()

	def test_axis_of_same_size(self):
		x_axis = np.arange(10)
		y_axis = np.arange(9)
		with pytest.raises(ValueError):
			Interpolation(x_axis=x_axis, y_axis=y_axis)

	def test_raises_error_if_no_new_array(self):
		x_axis = np.arange(10)
		y_axis = np.arange(10) + 5
		o_interpolation = Interpolation(x_axis=x_axis, y_axis=y_axis)

		with pytest.raises(ValueError):
			o_interpolation.get_new_y_array()

	@pytest.mark.parametrize('x_axis, y_axis, new_x_axis, new_y_axis',
	                         [(np.arange(10), np.arange(10)+5, np.arange(0, 10, 2), np.arange(0, 10, 2)+5),
	                          (np.arange(10), np.arange(10)+5, np.arange(0.3, 9, 0.6), [5.3, 5.9, 6.5, 7.1, 7.7,
	                                                                                    8.3, 8.9, 9.5, 10.1, 10.7,
	                                                                                    11.3, 11.9, 12.5, 13.1])])
	def test_right_new_x_axis_generated(self, x_axis, y_axis, new_x_axis, new_y_axis):
		o_interpolation = Interpolation(x_axis=x_axis, y_axis=y_axis)
		y_axis_calculated = o_interpolation.get_new_y_array(new_x_axis=new_x_axis)

		assert all([abs(a-b) < EPS for a, b in zip(new_y_axis, y_axis_calculated)])

	@pytest.mark.parametrize('new_x_axis', [np.arange(-1, 2), np.arange(2, 15), np.arange(-3, 17)])
	def test_new_x_axis_within_old_x_range(self, new_x_axis):
		x_axis = np.arange(10)
		y_axis = np.arange(10)+5

		o_interpolation = Interpolation(x_axis=x_axis, y_axis=y_axis)
		with pytest.raises(ValueError):
			o_interpolation.get_new_y_array(new_x_axis=new_x_axis)

