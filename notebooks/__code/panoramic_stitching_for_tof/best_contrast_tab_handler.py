import numpy as np
from qtpy.QtWidgets import QApplication
from qtpy import QtCore, QtGui
import os


class BestContrastTabHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def display_selected_folder(self):
        folder_name = self.parent.ui.list_folders_combobox.currentText()

        if self.parent.ui.raw_image_radioButton.isChecked():
            image = self.parent.integrated_images[folder_name].data
        else:
            image = self.parent.best_contrast_images[folder_name]

        # _view = self.parent.ui.image_view_best_contrast.getView()
        # _view_box = _view.getViewBox()
        # _state = _view_box.getState()
        #
        # first_update = False
        # if self.parent.histogram_level_best_contrast is None:
        #     first_update = True
        # _histo_widget = self.parent.ui.image_view_best_contrast.getHistogramWidget()
        # self.parent.histogram_level_best_contrast = _histo_widget.getLevels()

        _image = np.transpose(image)
        self.parent.ui.image_view_best_contrast.setImage(_image)
        self.parent.current_live_image_best_contrast = _image
        # _view_box.setState(_state)

        # if not first_update:
        #     _histo_widget.setLevels(self.parent.histogram_level_best_contrast[0],
        #                             self.parent.histogram_level_best_contrast[1])

    def calculate_best_contrast(self):
        nbr_images = self.parent.nbr_files_per_folder
        bin_size = np.int(self.parent.ui.best_contrast_bin_size_value.text())
        list_bin = np.arange(0, nbr_images, bin_size)

        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        nbr_folders = len(self.parent.list_folders*2)
        self.parent.eventProgress.setMaximum(nbr_folders)
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)

        best_contrast_images = {}
        all_data = {}
        progress_index = 0
        for _folder in self.parent.list_folders:
            folder_key = os.path.basename(_folder)
            tmp_all_data = [self.parent.data_dictionary[folder_key][_key].data
                            for _key in self.parent.data_dictionary[folder_key].keys()]
            # remove first 100 and last 100 (too noisy)
            all_data[folder_key] = tmp_all_data[100:-100]

            self.parent.eventProgress.setValue(progress_index)
            progress_index += 1
            QtGui.QGuiApplication.processEvents()

        for _folder in self.parent.list_folders:
            left_bin_index = 0
            folder_key = os.path.basename(_folder)
            all_data_of_folder = all_data[folder_key]

            list_mean_counts_of_bin = []
            while left_bin_index < len(list_bin)-1:
                data_bin = all_data_of_folder[list_bin[left_bin_index]:list_bin[left_bin_index+1]]
                mean_data_bin = np.nanmean(data_bin)
                list_mean_counts_of_bin.append(mean_data_bin)
                left_bin_index += 1

            best_bin_index = {'numerator': 0, 'denominator': 0}

            max_ratio_value = 0
            for _bin_index_numerator in np.arange(len(list_bin)-1):
                for _bin_index_denominator in np.arange(len(list_bin)-1):
                    bin_ratio = list_mean_counts_of_bin[_bin_index_numerator] / \
                                list_mean_counts_of_bin[_bin_index_denominator]
                    diff_with_1 = np.abs(1 - bin_ratio)

                    if diff_with_1 > max_ratio_value:
                        max_ratio_value = diff_with_1
                        best_bin_index['numerator'] = _bin_index_numerator
                        best_bin_index['denominator'] = _bin_index_denominator

            image1 = all_data_of_folder[list_bin[best_bin_index['numerator']]:
                                        list_bin[best_bin_index['numerator']+1]]
            image_numerator_mean = np.mean(image1, axis=0)

            image2 = all_data_of_folder[list_bin[best_bin_index['denominator']]:
                                        list_bin[best_bin_index['denominator'] + 1]]
            image_denominator_mean = np.mean(image2, axis=0)

            index_of_0 = np.where(image_denominator_mean == 0)
            image_denominator_mean[index_of_0] = np.NaN

            best_contrast_images[_folder] = np.true_divide(image_numerator_mean, image_denominator_mean)

            self.parent.eventProgress.setValue(progress_index)
            progress_index += 1
            QtGui.QGuiApplication.processEvents()

        self.parent.best_contrast_images = best_contrast_images

        self.parent.eventProgress.setVisible(False)
        self.parent.ui.best_contrast_image_radioButton.setEnabled(True)
        self.parent.ui.statusbar.showMessage("Done calculating the best contrast images!", 10000)
        QApplication.restoreOverrideCursor()
