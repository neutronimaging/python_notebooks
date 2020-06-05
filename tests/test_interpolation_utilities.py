import pytest
import numpy as np

from __code.interpolation_utilities import Interpolation


class TestInterpolation:

	def test_minimum_axis_given(self):
		with pytest.raises(ValueError):
			Interpolation()

	def test_axis_of_same_size(self):
		x_axis = np.arange(10)
		y_axis = np.arange(9)
		with pytest.raises(ValueError):
			Interpolation(x_axis=x_axis, y_axis=y_axis)

	def test_same_output_if_no_increment(self):
		x_axis = np.arange(10)
		y_axis = np.arange(10) + 5
		o_interpolation = Interpolation(x_axis=x_axis, y_axis=y_axis)
		new_x_axis, new_y_axis = o_interpolation.get_new_array()

		assert all([a == b for a, b in zip(x_axis, new_x_axis)])
		assert all([a == b for a, b in zip(y_axis, new_y_axis)])

	@pytest.mark.parametrize('x_axis, y_axis, x_axis_increment, new_x_axis',
	                         [(np.arange(10), np.arange(10)+5, 2, np.arange(0, 10, 2))])
	def test_right_new_x_axis_generated(self, x_axis, y_axis, x_axis_increment, new_x_axis):
		o_interpolation = Interpolation(x_axis=x_axis, y_axis=y_axis)
		x_axis_returned, _ = o_interpolation.get_new_array(x_axis_increment=x_axis_increment)

		x_axis_expected = np.arange(0, 10, 2)
		assert all([a == b for a, b in zip(x_axis_returned, x_axis_expected)])



