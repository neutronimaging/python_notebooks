import copy
import numpy as np
from scipy import interpolate

from __code.mcp_chips_corrector import CHIP_CORRECTION, MCP_LOW_MODE, CHIP_GAP


class Alignment:

    raw_image = None
    chip_width = None
    chip_height = None

    def __init__(self, parent=None, raw_image=None):
        self.parent = parent
        self.raw_image = raw_image

        chip_size = self.get_chip_size()
        self.chip_width = chip_size['width']
        self.chip_height = chip_size['height']

    def correct(self):
        moved_image = self.move_chips(input_image=self.raw_image)
        fill_image = self.fill_gaps(moved_image=moved_image,
                                    raw_image=self.raw_image)
        return fill_image

    def fill_gaps(self, moved_image=None, raw_image=None):
        if moved_image is None:
            raise ValueError("no moved image provided to fill_gaps")
        if raw_image is None:
            raise ValueError("no raw image provided to fill gaps")

        # vertical gap
        chip1 = self.get_chip(chip_index=1)
        chip2 = self.get_chip(chip_index=2)
        size_of_gap = CHIP_GAP['low']['xoffset']

        x_axis_left = np.zeros(self.chip_height) + self.chip_width
        y_axis_left = np.arange(self.chip_height)

        x_axis_right = np.zeros(self.chip_height)
        y_axis_right = y_axis_left

        






        return []

    def move_chips(self, input_image=None):
        if input_image is None:
            raise ValueError("no input image provided to move_chips!")

        image_height, image_width = self.parent.image_size.height, \
                                    self.parent.image_size.width

        if image_height == MCP_LOW_MODE:
            mode = 'low'
        else:
            mode = 'high'

        chip_width = self.chip_width
        chip_height = self.chip_height

        chip1 = self.get_chip(chip_index=1)
        chip2 = self.get_chip(chip_index=2)
        chip3 = self.get_chip(chip_index=3)
        chip4 = self.get_chip(chip_index=4)

        list_xoffset = [CHIP_CORRECTION[mode][key]['xoffset'] for
                        key in CHIP_CORRECTION[mode].keys()]
        max_xoffset = np.max(list_xoffset)

        list_yoffset = [CHIP_CORRECTION[mode][key]['yoffset'] for
                        key in CHIP_CORRECTION[mode].keys()]
        max_yoffset = np.max(list_yoffset)

        new_image = np.zeros((image_height + max_yoffset,
                              image_width + max_xoffset))

        new_image[0: chip_height, 0:chip_width] = chip1
        new_image[CHIP_CORRECTION[mode][2]['yoffset']:
                  CHIP_CORRECTION[mode][2]['yoffset'] + chip_height,
                  chip_width + CHIP_CORRECTION[mode][2]['xoffset']:
                  CHIP_CORRECTION[mode][2]['xoffset'] + 2*chip_width] = chip2
        new_image[CHIP_CORRECTION[mode][3]['yoffset'] + chip_height:
                  CHIP_CORRECTION[mode][3]['yoffset'] + 2*chip_height,
                  CHIP_CORRECTION[mode][3]['xoffset']:
                  CHIP_CORRECTION[mode][3]['xoffset'] + chip_width] = chip3
        new_image[CHIP_CORRECTION[mode][4]['yoffset'] + chip_height:
                  CHIP_CORRECTION[mode][4]['yoffset'] + 2 * chip_height,
                  CHIP_CORRECTION[mode][4]['xoffset'] + chip_width:
                  CHIP_CORRECTION[mode][4]['xoffset'] + 2 * chip_width] = chip4

        return new_image

    def get_chip(self, chip_index=1):

        raw_image = self.raw_image

        image_height, image_width = self.parent.image_size.height, \
                                    self.parent.image_size.width

        chip_width = self.chip_width
        chip_height = self.chip_height

        if chip_index == 1:
            return raw_image[0: chip_height, 0: chip_width]

        elif chip_index == 2:
            return raw_image[0: chip_height, chip_width:image_width]
        elif chip_index == 3:
            return raw_image[chip_height: image_height, 0: chip_width]
        elif chip_index == 4:
            return raw_image[chip_height: image_height, chip_width: image_width]
        else:
            raise ValueError("chip index does not exist!")

    def get_chip_size(self):
        image_height, image_width = self.parent.image_size.height, \
                                    self.parent.image_size.width

        mid_width = np.int(image_width / 2)
        mid_height = np.int(image_height / 2)

        return {'width': mid_width, 'height': mid_height}

    # @staticmethod
    # def get_a(y0=0, x0=0, y1=1, x1=1):
    #     a = (y1 - y0) / (x1 - x0)
    #     return a
    #
    # @staticmethod
    # def get_b(y0=0, x0=0, y1=1, x1=1):
    #     a = Alignment.get_a(y0=y0, x0=x0, y1=y1, x1=x1)
    #     b = y1 - a * x1
    #     return b
    #
    # @staticmethod
    # def linear_equation(x=0, a=0, b=0):
    #     return a * x + b

    @staticmethod
    def get_interpolated_value(x0=0, x1=1, value_x0=5, value_x1=10, list_value_x=[np.NaN]):
        A = (x0, value_x0)
        B = (x1, value_x1)
        f = interpolate.interp1d(A, B)
        result = f(list_value_x)
        return result
