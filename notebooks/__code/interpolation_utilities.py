from scipy import interpolate


class Interpolation:

	def __init__(self, x_axis=None, y_axis=None):
		if (x_axis is None) or (y_axis is None):
			raise ValueError("Please provide both x and y-axis")

		if (len(x_axis) != len(y_axis)):
			raise ValueError("Axis must have the same size")

		self.x_axis = x_axis
		self.y_axis = y_axis

	def get_new_y_array(self, new_x_axis=None):
		if new_x_axis is None:
			raise ValueError("Please provide a new x_axis!")

		x_axis = self.x_axis
		y_axis = self.y_axis

		if (new_x_axis[0] < x_axis[0]) or (new_x_axis[-1] > x_axis[-1]):
			raise ValueError("New x axis mus tbe inside old x_axis")

		tck = interpolate.splrep(x_axis, y_axis, s=0)
		new_y_axis = interpolate.splev(new_x_axis, tck, der=0)

		return new_y_axis
