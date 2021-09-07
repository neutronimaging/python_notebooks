import pytest

from notebooks.__code._utilities import math


class TestMath:

    def test_get_distance_needs_right_arguments(self):
        with pytest.raises(ValueError):
            math.get_distance_between_two_points()

    @pytest.mark.parametrize('from_pixel, to_pixel, distance_expected',
                             [({'x': 0, 'y': 0}, {'x': 6, 'y': 0}, 6),
                              ({'x': 6, 'y': 0}, {'x': 0, 'y': 0}, 6),
                              ({'x': 0, 'y': 0}, {'x': 0, 'y': 6}, 6),
                              ({'x': 6, 'y': 6}, {'x': 0, 'y': 0}, 8.485)])
    def test_get_distance(self, from_pixel, to_pixel, distance_expected):
        distance_calculated = math.get_distance_between_two_points(from_x=from_pixel['x'],
                                                                   from_y=from_pixel['y'],
                                                                   to_x=to_pixel['x'],
                                                                   to_y=to_pixel['y'])
        assert distance_calculated == pytest.approx(distance_expected, 1e-2)
