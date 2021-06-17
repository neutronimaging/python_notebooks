import copy
import numpy as np

from __code.mcp_chips_corrector import chip_correction, MCP_LOW_MODE


class Alignment:

    def __init__(self, parent=None):
        self.parent = parent

    def correct(self, input_image=None):
        if input_image is None:
            raise ValueError("no input image provided!")

        raw_image = copy.deepcopy(input_image)
        image_height, image_width = self.parent.image_size.height, self.parent.image_size.width

        if image_height == MCP_LOW_MODE:
            mode = 'low'
        else:
            mode = 'high'

        mid_width = np.int(image_width/2)
        mid_height = np.int(image_height/2)

        chip1 = raw_image[0: mid_height, 0: mid_width]
        chip2 = raw_image[0: mid_height, mid_width:image_width]
        chip3 = raw_image[mid_height: image_height, 0: mid_width]
        chip4 = raw_image[mid_height: image_height, mid_width: image_width]

        list_xoffset = [chip_correction[mode][key]['xoffset'] for
                        key in chip_correction[mode].keys()]
        max_xoffset = np.max(list_xoffset)

        list_yoffset = [chip_correction[mode][key]['yoffset'] for
                        key in chip_correction[mode].keys()]
        max_yoffset = np.max(list_yoffset)

        new_image = np.zeros((image_height + max_yoffset,
                              image_width + max_xoffset))

        new_image[0: mid_height, 0:mid_width] = chip1
        new_image[chip_correction[mode][2]['yoffset']:
                  chip_correction[mode][2]['yoffset'] + mid_height,
                  mid_width + chip_correction[mode][2]['xoffset']:
                  chip_correction[mode][2]['xoffset'] + 2*mid_width] = chip2
        new_image[chip_correction[mode][3]['yoffset'] + mid_height:
                  chip_correction[mode][3]['yoffset'] + 2*mid_height,
                  chip_correction[mode][3]['xoffset']:
                  chip_correction[mode][3]['xoffset'] + mid_width] = chip3
        new_image[chip_correction[mode][4]['yoffset'] + mid_height:
                  chip_correction[mode][4]['yoffset'] + 2 * mid_height,
                  chip_correction[mode][4]['xoffset'] + mid_width:
                  chip_correction[mode][4]['xoffset'] + 2 * mid_width] = chip4

        return new_image
