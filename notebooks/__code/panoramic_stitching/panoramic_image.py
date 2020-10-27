import numpy as np
import os

from __code._utilities.table_handler import TableHandler


class PanoramicImage:

    def __init__(self, parent=None):
        self.parent = parent

    def update_current_panoramic_image(self):
        folder_selected = os.path.basename(self.parent.ui.list_folders_combobox.currentText())

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

    def get_max_offset(self, folder_selected=None):
        offset_dictionary = self.parent.offset_dictionary[folder_selected]

        list_xoffset = [offset_dictionary[_key]['xoffset'] for _key in offset_dictionary.keys()]
        list_yoffset = [offset_dictionary[_key]['yoffset'] for _key in offset_dictionary.keys()]

        return np.int(np.max(list_yoffset)), np.int(np.max(list_xoffset))
