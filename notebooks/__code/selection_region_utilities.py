from collections import OrderedDict


class SelectionRegionUtilities:

	def __init__(self, x0=None, y0=None, width=None, height=None):
		"""it's up to the user to make sure the width and height are real positive numbers and that
		x0 and y0 are also real and defined"""
		self.x0 = x0
		self.y0 = y0
		self.width = width
		self.height = height

	def get_all_russian_doll_regions(self):
		"""this return a dictionary of all the region contains inside the given selection, recursively
		The last region will have to be always 1 pixel wide, or height, or both
		"""
		x0 = self.x0
		y0 = self.y0
		width = self.width
		height = self.height

		dict_regions = OrderedDict()
		dict_regions[0] = {'x0': x0, 'y0': y0, 'width': width, 'height': height}
		index = 1

		while width + height > 2:
			x0, y0, width, height = self.produce_next_doll_region(x0, y0, width, height)
			dict_regions[index] = {'x0': x0, 'y0': y0, 'width': width, 'height': height}
			index += 1

		return dict_regions

	@staticmethod
	def produce_next_doll_region(x0, y0, width, height):
		new_width = 1 if (width == 1 or width == 2) else width-2
		new_height = 1 if (height == 1 or height == 2) else height-2

		new_x0 = x0 if (new_width == width) else x0+1
		new_y0 = y0 if (new_height == height) else y0+1

		return new_x0, new_y0, new_width, new_height
