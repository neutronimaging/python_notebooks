import numpy as np


class Color(object):

    list_rgb = [[0, 0, 255],  # dark blue
                [30, 100, 100], # orange
                [180, 100, 100], # cyan
                [100, 100, 100], # light green
                [70, 100, 100], # yellow
                [128, 250, 227], # light cyan
                [11, 50, 100], # light pink
                [250, 128, 247], # pink
                [128, 128, 248], # purple blue
                [159, 255, 128], # light green
                ]

    list_matplotlib = ['b', 'g', 'r', 'c', 'm', 'y']

    def get_list_rgb(self, nbr_color=10):
        list_rgb = []

        # make sure we will produce enough color
        nbr_rgb = len(self.list_rgb)
        repetition = np.int(np.divide(nbr_color, nbr_rgb)) + 1

        for _ in np.arange(repetition):
            for _color in self.list_rgb:
                list_rgb.append(_color)

        return list_rgb


