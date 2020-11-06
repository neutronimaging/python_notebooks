import os
from qtpy.QtWidgets import QFileDialog
from qtpy import QtGui
import numpy as np
from collections import OrderedDict

from __code.file_handler import make_or_reset_folder


class Export:

    def __init__(self, parent=None):
        self.parent = parent

    def run(self):
        output_folder = QFileDialog.getExistingDirectory(self.parent,
                                                         directory=self.parent.working_dir,
                                                         caption="Select where the folder containing the "
                                                                   "panoramic images will be created!",
                                                         options=QFileDialog.ShowDirsOnly)

        if output_folder:
            self._export(output_folder=output_folder)

    def _export(self, output_folder=None):
        data_dictionary = self.parent.data_dictionary
        offset_dictionary = self.parent.offset_dictionary

        new_output_folder_name = os.path.join(output_folder,
                                              os.path.basename(self.parent.working_dir) + "_panoramic")

        make_or_reset_folder(new_output_folder_name)

        nbr_group = len(data_dictionary.keys())
        self.parent.eventProgress.setMaximum(nbr_group)
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)

        panoramic_height, panoramic_width = np.shape(self.parent.current_live_image)
        image_height = self.parent.image_height
        image_width = self.parent.image_width

        panoramic_images = OrderedDict()

        for _group_index, _group_name in enumerate(data_dictionary.keys()):

            panoramic_image = np.zeros(panoramic_height, panoramic_width)

            data_dictionary_of_group = data_dictionary[_group_name]
            offset_dictionary_of_group = offset_dictionary[_group_name]

            for _file_index, _file in enumerate(data_dictionary.keys()):

                yoffset = offset_dictionary_of_group[_file]['yoffset']
                xoffset = offset_dictionary_of_group[_file]['xoffset']
                image = data_dictionary_of_group['file'].data

                if _file_index == 0:
                    panoramic_image[yoffset: yoffset+image_height,
                    xoffset: xoffset+image_width] = image
                    continue

                temp_big_image = np.zeros(panoramic_height, panoramic_width)
                temp_big_image[yoffset: yoffset+image_height,
                xoffset: xoffset+image_width] = image

                where_panoramic_image_has_value_only = np.where((panoramic_image != 0) & (temp_big_image == 0))
                where_temp_big_image_has_value_only = np.where((temp_big_image != 0) & (panoramic_image == 0))
                where_both_images_overlap = np.where((panoramic_image != 0) & (temp_big_image != 0))

                panoramic_image[where_temp_big_image_has_value_only] = \
                    temp_big_image[where_temp_big_image_has_value_only]
                panoramic_image[where_both_images_overlap] = (panoramic_image[where_both_images_overlap] +
                                                              temp_big_image[where_both_images_overlap]) / 2

            panoramic_image[_group_name] = panoramic_image

            self.parent.eventProgress.setValue(_group_index + 1)
            QtGui.QGuiApplication.processEvents()

        self.parent.panoramic_images = panoramic_image

        self.parent.eventProgress.setVisible(False)


