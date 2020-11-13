import os
from qtpy.QtWidgets import QFileDialog
from qtpy import QtGui
import numpy as np
from collections import OrderedDict
import glob

from NeuNorm.normalization import Normalization

from __code.file_handler import make_or_reset_folder
from __code.panoramic_stitching_for_tof.image_handler import HORIZONTAL_MARGIN, VERTICAL_MARGIN
from __code.file_handler import copy_and_rename_files_to_folder

FILE_PREFIX = "image_"


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

        list_folder = list(data_dictionary.keys())
        nbr_files = len(data_dictionary[list_folder[0]].keys())

        self.parent.eventProgress.setMaximum(nbr_files)
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)

        # width, height because we did a transpose to display current_live_image correctly
        panoramic_width, panoramic_height = np.shape(self.parent.current_live_image)
        image_height = self.parent.image_height
        image_width = self.parent.image_width

        panoramic_images_dict = OrderedDict()
        self.parent.ui.statusbar.showMessage("Create the panoramic images ...")
        QtGui.QGuiApplication.processEvents()

        for _file_index in np.arange(nbr_files):
            panoramic_image = np.zeros((panoramic_height, panoramic_width))
            for _folder_index, _folder in enumerate(data_dictionary.keys()):

                xoffset = offset_dictionary[_folder]['xoffset']
                yoffset = offset_dictionary[_folder]['yoffset']

                list_files = list(data_dictionary[_folder].keys())

                image = data_dictionary[_folder][list_files[_file_index]].data

                if _folder_index == 0:
                    panoramic_image[yoffset+VERTICAL_MARGIN: yoffset+image_height+VERTICAL_MARGIN,
                    xoffset+HORIZONTAL_MARGIN: xoffset+image_width+HORIZONTAL_MARGIN] = image
                    continue

                temp_big_image = np.zeros((panoramic_height, panoramic_width))

                temp_big_image[yoffset+VERTICAL_MARGIN: yoffset+image_height+VERTICAL_MARGIN,
                xoffset+HORIZONTAL_MARGIN: xoffset+image_width+HORIZONTAL_MARGIN] = image

                where_temp_big_image_has_value_only = np.where((temp_big_image != 0) & (panoramic_image == 0))
                where_both_images_overlap = np.where((panoramic_image != 0) & (temp_big_image != 0))

                panoramic_image[where_temp_big_image_has_value_only] = \
                    temp_big_image[where_temp_big_image_has_value_only]
                panoramic_image[where_both_images_overlap] = (panoramic_image[where_both_images_overlap] +
                                                              temp_big_image[where_both_images_overlap]) / 2

            file_name = FILE_PREFIX + "{:04d}.tiff".format(_file_index)
            panoramic_images_dict[file_name] = panoramic_image

            self.parent.eventProgress.setValue(_file_index + 1)
            QtGui.QGuiApplication.processEvents()

        self.parent.panoramic_images_to_export = panoramic_images_dict
        self.parent.eventProgress.setVisible(False)

    def export_images(self, output_folder=None):

        new_folder_name = os.path.basename(self.parent.working_dir) + "_panoramic"
        self.parent.ui.statusbar.showMessage("Exporting images in folder {}".format(new_folder_name))
        QtGui.QGuiApplication.processEvents()

        new_output_folder_name = os.path.join(output_folder, new_folder_name)

        make_or_reset_folder(new_output_folder_name)
        panoramic_images_dict = self.parent.panoramic_images_to_export

        list_data = []
        list_filename = []
        for _file_name in panoramic_images_dict.keys():
            list_data.append(panoramic_images_dict[_file_name])
            list_filename.append(_file_name)

        o_norm = Normalization()
        o_norm.load(data=list_data)
        o_norm.data['sample']['filename'] = list_filename
        o_norm.export(new_output_folder_name, data_type='sample')

        self.copy_txt_files_to_output_folder(output_folder=new_output_folder_name)

        self.parent.ui.statusbar.showMessage("{} has been created!".format(new_output_folder_name), 10000)  # 10s
        QtGui.QGuiApplication.processEvents()

    def copy_txt_files_to_output_folder(self, output_folder=None):
        list_input_folders = self.parent.list_folders
        first_folder = list_input_folders[0]
        list_txt_files = glob.glob(first_folder + "/*.txt")

        list_new_file_names = []

        for txt_file in list_txt_files:
            split_name = os.path.basename(txt_file).split("_")
            new_name = split_name[-1]
            list_new_file_names.append(new_name)

        copy_and_rename_files_to_folder(list_files=list_txt_files,
                                        new_list_files_names=list_new_file_names,
                                        output_folder=output_folder)
