import os
from qtpy.QtWidgets import QFileDialog
from qtpy import QtGui
import numpy as np
from collections import OrderedDict

from NeuNorm.normalization import Normalization

from __code.file_handler import make_or_reset_folder
from __code.panoramic_stitching.image_handler import HORIZONTAL_MARGIN, VERTICAL_MARGIN


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
            self.parent.ui.setEnabled(False)
            QtGui.QGuiApplication.processEvents()
            self.create_panoramic_images()
            self.export_images(output_folder=output_folder)
            self.parent.ui.setEnabled(True)

    def create_panoramic_images(self, output_folder=None):
        data_dictionary = self.parent.data_dictionary
        offset_dictionary = self.parent.offset_dictionary

        nbr_group = len(data_dictionary.keys())
        self.parent.eventProgress.setMaximum(nbr_group)
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)

        panoramic_height, panoramic_width = np.shape(self.parent.current_live_image)
        image_height = self.parent.image_height
        image_width = self.parent.image_width

        panoramic_images_dict = OrderedDict()

        for _group_index, _group_name in enumerate(data_dictionary.keys()):

            self.parent.ui.statusbar.showMessage("Creating panoramic image of {} in progress...".format(_group_name))

            panoramic_image = np.zeros((panoramic_height, panoramic_width))

            data_dictionary_of_group = data_dictionary[_group_name]
            offset_dictionary_of_group = offset_dictionary[_group_name]

            for _file_index, _file in enumerate(data_dictionary_of_group.keys()):

                yoffset = offset_dictionary_of_group[_file]['yoffset']
                xoffset = offset_dictionary_of_group[_file]['xoffset']
                image = data_dictionary_of_group[_file].data

                if _file_index == 0:
                    panoramic_image[yoffset+VERTICAL_MARGIN: yoffset+image_height+VERTICAL_MARGIN,
                    xoffset+HORIZONTAL_MARGIN: xoffset+image_width+HORIZONTAL_MARGIN] = image
                    continue

                temp_big_image = np.zeros((panoramic_height, panoramic_width))
                temp_big_image[yoffset+VERTICAL_MARGIN: yoffset+image_height+VERTICAL_MARGIN,
                xoffset+HORIZONTAL_MARGIN: xoffset+image_width+HORIZONTAL_MARGIN] = image

                # where_panoramic_image_has_value_only = np.where((panoramic_image != 0) & (temp_big_image == 0))
                where_temp_big_image_has_value_only = np.where((temp_big_image != 0) & (panoramic_image == 0))
                where_both_images_overlap = np.where((panoramic_image != 0) & (temp_big_image != 0))

                panoramic_image[where_temp_big_image_has_value_only] = \
                    temp_big_image[where_temp_big_image_has_value_only]
                panoramic_image[where_both_images_overlap] = (panoramic_image[where_both_images_overlap] +
                                                              temp_big_image[where_both_images_overlap]) / 2

            panoramic_images_dict[_group_name] = panoramic_image

            self.parent.eventProgress.setValue(_group_index + 1)
            QtGui.QGuiApplication.processEvents()

        self.parent.panoramic_images = panoramic_images_dict

        self.parent.eventProgress.setVisible(False)

    def export_images(self, output_folder=None):

        new_folder_name = os.path.basename(self.parent.working_dir) + "_panoramic"
        self.parent.ui.statusbar.showMessage("Exporting images in folder {}".format(new_folder_name))
        new_output_folder_name = os.path.join(output_folder, new_folder_name)

        make_or_reset_folder(new_output_folder_name)
        panoramic_images_dict = self.parent.panoramic_images

        list_data = []
        list_filename = []
        for _key in panoramic_images_dict.keys():
            list_data.append(panoramic_images_dict[_key])
            list_filename.append(_key)

        o_norm = Normalization()
        o_norm.load(data=list_data)
        o_norm.data['sample']['filename'] = list_filename
        o_norm.export(new_output_folder_name, data_type='sample')
        self.parent.ui.statusbar.showMessage("{} has been created!".format(new_output_folder_name), 10000)  # 10s
