import os
from qtpy.QtWidgets import QFileDialog, QDialog, QMainWindow
from qtpy import QtGui
import numpy as np
from collections import OrderedDict

from NeuNorm.normalization import Normalization
from notebooks.__code import load_ui

from __code.file_handler import make_or_reset_folder
from __code.panoramic_stitching.image_handler import HORIZONTAL_MARGIN, VERTICAL_MARGIN
from __code.panoramic_stitching.stitching_algorithms import StitchingAlgorithmType


class Export:

    def __init__(self, parent=None):
        self.parent = parent

    def run(self):
        self.parent.setEnabled(False)
        o_dialog = SelectStitchingAlgorithm(top_parent=self.parent, parent=self)
        o_dialog.show()

    def select_output_folder(self):
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

        # width then height due to the transpose before saving current_live_image (to get plot correctly displayed)
        panoramic_width, panoramic_height = np.shape(self.parent.current_live_image)
        image_height = self.parent.image_height
        image_width = self.parent.image_width

        panoramic_images_dict = OrderedDict()
        stitching_algorithm = self.parent.stitching_algorithm

        for _group_index, _group_name in enumerate(data_dictionary.keys()):

            self.parent.ui.statusbar.showMessage("Creating panoramic image of {} using algo. {} in progress...".format(
                    _group_name, self.parent.stitching_algorithm))
            QtGui.QGuiApplication.processEvents()
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

                if stitching_algorithm == StitchingAlgorithmType.minimum:

                    panoramic_image[where_temp_big_image_has_value_only] = \
                        temp_big_image[where_temp_big_image_has_value_only]
                    panoramic_image[where_both_images_overlap] = np.minimum(panoramic_image[where_both_images_overlap],
                                                                            temp_big_image[where_both_images_overlap])

                elif stitching_algorithm == StitchingAlgorithmType.maximum:

                    panoramic_image[where_temp_big_image_has_value_only] = \
                        temp_big_image[where_temp_big_image_has_value_only]
                    panoramic_image[where_both_images_overlap] = np.maximum(panoramic_image[where_both_images_overlap],
                                                                            temp_big_image[where_both_images_overlap])

                elif stitching_algorithm == StitchingAlgorithmType.mean:

                    panoramic_image[where_temp_big_image_has_value_only] = \
                        temp_big_image[where_temp_big_image_has_value_only]
                    panoramic_image[where_both_images_overlap] = (panoramic_image[where_both_images_overlap] +
                                                                  temp_big_image[where_both_images_overlap])/2

            panoramic_images_dict[_group_name] = panoramic_image

            self.parent.eventProgress.setValue(_group_index + 1)
            QtGui.QGuiApplication.processEvents()

        self.parent.panoramic_images = panoramic_images_dict

        self.parent.eventProgress.setVisible(False)

    def export_images(self, output_folder=None):

        stitching_algorithm = self.parent.stitching_algorithm
        new_folder_name = os.path.basename(self.parent.working_dir) + "_panoramic_{}".format(stitching_algorithm)
        self.parent.ui.statusbar.showMessage("Exporting images in folder {}".format(new_folder_name))
        QtGui.QGuiApplication.processEvents()
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


class SelectStitchingAlgorithm(QDialog):

    stitching_algorithm = StitchingAlgorithmType.minimum

    def __init__(self, top_parent=None, parent=None):
        self.parent = parent
        self.top_parent = top_parent
        QDialog.__init__(self, parent=top_parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui', 'ui_panoramic_stitching_algorithms.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)

    def use_minimum_counts_clicked(self):
        self.activate_radio_button(button_to_activate='minimum_counts')

    def use_maximum_counts_clicked(self):
        self.activate_radio_button(button_to_activate='maximum_counts')

    def use_mean_counts_clicked(self):
        self.activate_radio_button(button_to_activate='mean_counts')

    def activate_radio_button(self, button_to_activate='minimum_counts'):
        self.ui.use_minimum_radioButton.setChecked(False)
        self.ui.use_maximum_radioButton.setChecked(False)
        self.ui.use_mean_radioButton.setChecked(False)
        if button_to_activate == 'minimum_counts':
            self.ui.use_minimum_radioButton.setChecked(True)
        elif button_to_activate == 'maximum_counts':
            self.ui.use_maximum_radioButton.setChecked(True)
        elif button_to_activate == 'mean_counts':
            self.ui.use_mean_radioButton.setChecked(True)

    def closeEvent(self, c):
        self.top_parent.setEnabled(True)

    def exit(self):
        self.closeEvent(None)
        self.close()

    def ok_pushed(self):
        self.top_parent.stitching_algorithm = self._get_stitching_algorithm_selected()
        self.close()
        self.top_parent.setEnabled(True)
        self.parent.select_output_folder()

    def _get_stitching_algorithm_selected(self):
        if self.ui.use_minimum_radioButton.isChecked():
            return StitchingAlgorithmType.minimum
        elif self.ui.use_maximum_radioButton.isChecked():
            return StitchingAlgorithmType.maximum
        elif self.ui.use_mean_radioButton.isChecked():
            return StitchingAlgorithmType.mean
        elif self.ui.use_linear_integration_radioButton.isChecked():
            return StitchingAlgorithmType.linear_integration
        else:
            raise NotImplementedError("Stitching algorithm has not been implemented yet!")
