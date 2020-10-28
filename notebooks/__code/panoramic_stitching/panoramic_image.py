import numpy as np
import os

from __code._utilities.table_handler import TableHandler
from __code.panoramic_stitching.get import Get


class PanoramicImage:

    def __init__(self, parent=None):
        self.parent = parent

    def update_current_panoramic_image(self):

        _view = self.parent.ui.image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()

        first_update = False
        if self.parent.histogram_level is None:
            first_update = True
        _histo_widget = self.parent.ui.image_view.getHistogramWidget()
        self.parent.histogram_level = _histo_widget.getLevels()

        o_get = Get(parent=self.parent)
        folder_selected = o_get.get_combobox_folder_selected()

        data_dictionary = self.parent.data_dictionary[folder_selected]
        offset_dictionary = self.parent.offset_dictionary[folder_selected]

        max_yoffset, max_xoffset = self.get_max_offset(folder_selected=folder_selected)

        image_height = 0
        image_width = 0

        panoramic_image = None
        for _file_index, _file in enumerate(data_dictionary.keys()):
            _image = data_dictionary[_file].data
            if _file_index == 0:
                image_height, image_width = np.shape(_image)
                panoramic_image = np.zeros((max_yoffset + image_height, max_xoffset + image_width))
                panoramic_image[0:image_height, 0:image_width] = _image
            else:
                xoffset = offset_dictionary[_file]['xoffset']
                yoffset = offset_dictionary[_file]['yoffset']

                panoramic_image[yoffset: yoffset+image_height, xoffset: xoffset+image_width] = _image

        self.parent.panoramic_images[folder_selected] = panoramic_image

        _image = np.transpose(panoramic_image)
        # _image = self._clean_image(_image)
        self.parent.ui.image_view.setImage(_image)
        _view_box.setState(_state)

        if not first_update:
            _histo_widget.setLevels(self.parent.histogram_level[0],
                                    self.parent.histogram_level[1])

    def get_max_offset(self, folder_selected=None):
        offset_dictionary = self.parent.offset_dictionary[folder_selected]

        list_xoffset = [offset_dictionary[_key]['xoffset'] for _key in offset_dictionary.keys()]
        list_yoffset = [offset_dictionary[_key]['yoffset'] for _key in offset_dictionary.keys()]

        return np.int(np.max(list_yoffset)), np.int(np.max(list_xoffset))

