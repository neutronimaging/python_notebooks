import copy
import numpy as np
from scipy import interpolate
import logging

from __code.mcp_chips_corrector import CHIP_CORRECTION, MCP_LOW_MODE, CHIP_GAP, NBR_OF_EDGES_PIXEL_TO_NOT_USE


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
        fill_image = self.fill_gaps(moved_image=moved_image)
        return fill_image

    def fill_gaps(self, moved_image=None):

        if not self.parent.ui.auto_fill_gaps_checkBox.isChecked():
            return moved_image

        if moved_image is None:
            raise ValueError("no moved image provided to fill_gaps")

        logging.info(f"--> filling gaps")

        self._fix_vertical_gap(moved_image=moved_image,
                               first_chip_index=1,
                               second_chip_index=2,
                               image_mode='low')

        self._fix_vertical_gap(moved_image=moved_image,
                               first_chip_index=3,
                               second_chip_index=4,
                               image_mode='low')

        self._fix_horizontal_gap(moved_image=moved_image,
                                 first_chip_index=1,
                                 second_chip_index=3,
                                 image_mode='low')

        self._fix_horizontal_gap(moved_image=moved_image,
                                 first_chip_index=2,
                                 second_chip_index=4,
                                 image_mode='low')

        return moved_image

    def _fix_vertical_gap(self, moved_image=None, first_chip_index=1, second_chip_index=2, image_mode='low'):

        logging.info(f"---> working on vertical gap chip{first_chip_index}/chip{second_chip_index}")
        chip_a = self.get_chip(chip_index=first_chip_index)
        chip_b = self.get_chip(chip_index=second_chip_index)
        size_of_gap = CHIP_GAP[image_mode]

        x_axis_left = np.zeros(self.chip_height) + self.chip_width - 1 - NBR_OF_EDGES_PIXEL_TO_NOT_USE
        y_axis_left = np.arange(self.chip_height)

        if (first_chip_index == 1) and (second_chip_index == 2):
            global_y_axis_left = y_axis_left

        elif (first_chip_index == 3) and (second_chip_index == 4):
            global_y_axis_left = np.arange(self.chip_height) + self.chip_height + size_of_gap['yoffset']

        x_axis_right = np.zeros(self.chip_height) + NBR_OF_EDGES_PIXEL_TO_NOT_USE
        y_axis_right = y_axis_left

        for index, y in enumerate(global_y_axis_left):

            # logging.debug(f"----> index: {index} and y: {y}")

            x_left = int(x_axis_left[index])
            y_left = int(y_axis_left[index])
            intensity_left = chip_a[y_left, x_left]

            x_right = int(x_axis_right[index])
            y_right = int(y_axis_right[index])
            intensity_right = chip_b[y_right, x_right]

            x0 = x_left
            x1 = x_left + size_of_gap['xoffset'] + 1 + 2 * NBR_OF_EDGES_PIXEL_TO_NOT_USE

            list_x_gap = np.arange(x0+1, x1)
            # logging.debug(f"-----> x0:{x0}, x1:{x1}, value_x0:{intensity_left}, value_x1:{intensity_right}")
            # logging.debug(f"-----> list_x_gap: {list_x_gap}")
            list_intensity_gap = Alignment.get_interpolated_value(x0=x0,
                                                                  x1=x1,
                                                                  value_x0=intensity_left,
                                                                  value_x1=intensity_right,
                                                                  list_value_x=list_x_gap)
            # logging.debug(f"------> list_intensity_gap: {list_intensity_gap}")
            for _x, _intensity in zip(list_x_gap, list_intensity_gap):
                moved_image[y, _x] = _intensity

    def _fix_horizontal_gap(self, moved_image=None, first_chip_index=1, second_chip_index=3, image_mode='low'):

        logging.info(f"---> working on horizontal gap chip{first_chip_index}/chip{second_chip_index}")
        chip_a = self.get_chip(chip_index=first_chip_index)
        chip_b = self.get_chip(chip_index=second_chip_index)
        size_of_gap = CHIP_GAP[image_mode]

        x_axis_top = np.arange(self.chip_width)
        y_axis_top = np.zeros(self.chip_width) + self.chip_height - 1 - NBR_OF_EDGES_PIXEL_TO_NOT_USE

        if (first_chip_index == 1) and (second_chip_index == 3):
            global_x_axis_top = x_axis_top

        elif (first_chip_index == 2) and (second_chip_index == 4):
            global_x_axis_top = np.arange(self.chip_width) + self.chip_width + size_of_gap['xoffset']

        x_axis_bottom = x_axis_top
        y_axis_bottom = np.zeros(self.chip_width) + NBR_OF_EDGES_PIXEL_TO_NOT_USE

        for index, x in enumerate(global_x_axis_top):

            logging.debug(f"----> index: {index} and x: {x}")

            x_top = int(x_axis_top[index])
            y_top = int(y_axis_top[index])
            intensity_top = chip_a[y_top, x_top]

            x_bottom = int(x_axis_bottom[index])
            y_bottom = int(y_axis_bottom[index])
            intensity_bottom = chip_b[y_bottom, x_bottom]

            y0 = y_top
            y1 = y_top + size_of_gap['yoffset'] + 1 + 2 * NBR_OF_EDGES_PIXEL_TO_NOT_USE

            list_y_gap = np.arange(y0+1, y1)
            logging.debug(f"-----> y0:{y0}, y1:{y1}, value_y0:{intensity_top}, value_y1:{intensity_bottom}")
            logging.debug(f"-----> list_y_gap: {list_y_gap}")
            list_intensity_gap = Alignment.get_interpolated_value(x0=y0,
                                                                  x1=y1,
                                                                  value_x0=intensity_top,
                                                                  value_x1=intensity_bottom,
                                                                  list_value_x=list_y_gap)
            logging.debug(f"------> list_intensity_gap: {list_intensity_gap}")
            for _y, _intensity in zip(list_y_gap, list_intensity_gap):
                logging.debug(f"------> _y:{_y}, x:{x}")
                moved_image[_y, x] = _intensity

    def move_chips(self, input_image=None):

        logging.info(f"--> moving chips")
        if input_image is None:
            raise ValueError("no input image provided to move_chips!")

        image_height, image_width = self.parent.image_size.height, self.parent.image_size.width

        if image_height == MCP_LOW_MODE:
            mode = 'low'
        else:
            mode = 'high'

        chip_width = self.chip_width
        chip_height = self.chip_height

        logging.debug(f"---> chip_width:{chip_width}, chip_height:{chip_height}")

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

        logging.debug(f"---> np.shape(new_image): {np.shape(new_image)}")

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

    @staticmethod
    def get_interpolated_value(x0=0, x1=1, value_x0=5, value_x1=10, list_value_x=[np.NaN]):

        # logging.debug(f"x0:{x0}, x1:{x1}. value_x0:{value_x0}, value_x1:{value_x1}, list_value:{list_value_x}")
        A = (x0, x1)
        B = (value_x0, value_x1)
        # logging.debug(f"A:{A}, B:{B}")
        f = interpolate.interp1d(A, B)
        result = f(list_value_x)
        # logging.debug(f"result: {result}")
        return result
