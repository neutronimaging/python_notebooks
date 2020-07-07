import pytest

from __code.selection_region_utilities import SelectionRegionUtilities


class TestSelectionRegionUtilities:

	def test_correctly_initialized(self):
		o_selection = SelectionRegionUtilities(x0=5, y0=10, width=15, height=20)
		assert o_selection.x0 == 5
		assert o_selection.y0 == 10
		assert o_selection.width == 15
		assert o_selection.height == 20

	@pytest.mark.parametrize('x0, y0, width, height, new_x0, new_y0, new_width, new_height',
	                         [(5, 10, 15, 20, 6, 11, 13, 18),
	                          (5, 10, 1, 4, 5, 11, 1, 2),
	                          (5, 10, 1, 1, 5, 10, 1, 1),
	                          (5, 10, 2, 2, 6, 11, 1, 1),
	                          (5, 10, 5, 1, 6, 10, 3, 1)],)
	def test_next_doll_region(self, x0, y0, width, height, new_x0, new_y0, new_width, new_height):
		x0_returned, y0_returned, width_returned, height_returned = \
			SelectionRegionUtilities.produce_next_doll_region(x0, y0, width, height)
		assert x0_returned == new_x0
		assert y0_returned == new_y0
		assert width_returned == new_width
		assert height_returned == new_height

	def test_all_russian_doll_regions_for_2_square_dolls(self):
		o_region = SelectionRegionUtilities(x0=5, y0=10, width=3, height=3)
		dict_regions = o_region.get_all_russian_doll_regions()
		assert len(dict_regions) == 2
		assert dict_regions[0] == {'x0': 5, 'y0': 10, 'width': 3, 'height': 3}
		assert dict_regions[1] == {'x0': 6, 'y0': 11, 'width': 1, 'height': 1}

	def test_all_russian_doll_regions_for_2_free_dolls(self):
		o_region = SelectionRegionUtilities(x0=5, y0=10, width=1, height=3)
		dict_regions = o_region.get_all_russian_doll_regions()
		assert len(dict_regions) == 2
		assert dict_regions[0] == {'x0': 5, 'y0': 10, 'width': 1, 'height': 3}
		assert dict_regions[1] == {'x0': 5, 'y0': 11, 'width': 1, 'height': 1}

	def test_all_russian_doll_regions_for_1_square_dolls(self):
		o_region = SelectionRegionUtilities(x0=5, y0=10, width=1, height=1)
		dict_regions = o_region.get_all_russian_doll_regions()
		assert len(dict_regions) == 1
		assert dict_regions[0] == {'x0': 5, 'y0': 10, 'width': 1, 'height': 1}

	def test_all_russian_doll_regions_for_3_free_dolls(self):
		o_region = SelectionRegionUtilities(x0=5, y0=10, width=5, height=3)
		dict_regions = o_region.get_all_russian_doll_regions()
		assert len(dict_regions) == 3
		assert dict_regions[0] == {'x0': 5, 'y0': 10, 'width': 5, 'height': 3}
		assert dict_regions[1] == {'x0': 6, 'y0': 11, 'width': 3, 'height': 1}
		assert dict_regions[2] == {'x0': 7, 'y0': 11, 'width': 1, 'height': 1}
