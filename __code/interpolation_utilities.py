class Interpolation:

	def __init__(self, x_axis=None, y_axis=None):
		if (x_axis is None) or (y_axis is None):
			raise ValueError("Please provide both x and y-axis")

		if (len(x_axis) != len(y_axis)):
			raise ValueError("Axis must have the same size")

		self.x_axis = x_axis
		self.y_axis = y_axis

	def get_new_array(self, x_axis_increment=None):
		if x_axis_increment is None:
			return (self.x_axis, self.y_axis)

		x_axis = self.x_axis
		new_x_axis = [x_axis[0]]

		_x = x_axis[0]
		while (new_x_axis[-1] < x_axis[-1]):
			_x += x_axis_increment
			new_x_axis.append(_x)

		return new_x_axis, self.y_axis