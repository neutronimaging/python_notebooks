import numpy as np
from qtpy.QtWidgets import QApplication
from qtpy import QtCore, QtGui
import os


class BestContrastTabHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def display_selected_folder(self):
        folder_name = self.parent.ui.list_folders_combobox.currentText()
        image = self.parent.integrated_images[folder_name].data

        _view = self.parent.ui.image_view_best_contrast.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()

        first_update = False
        if self.parent.histogram_level_best_contrast is None:
            first_update = True
        _histo_widget = self.parent.ui.image_view_best_contrast.getHistogramWidget()
        self.parent.histogram_level_best_contrast = _histo_widget.getLevels()

        _image = np.transpose(image)
        self.parent.ui.image_view_best_contrast.setImage(_image)
        self.parent.current_live_image_best_contrast = _image
        # _view_box.setState(_state)

        if not first_update:
            _histo_widget.setLevels(self.parent.histogram_level_best_contrast[0],
                                    self.parent.histogram_level_best_contrast[1])

    def calculate_best_contrast(self):
        nbr_images = self.parent.nbr_files_per_folder
        bin_size = np.int(self.parent.ui.best_contrast_bin_size_value.text())
        list_bin = np.arange(0, nbr_images, bin_size)

        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        nbr_folders = len(self.parent.list_folders*2)
        self.parent.eventProgress.setMaximum(nbr_folders)
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)

        all_data = {}
        progress_index = 0
        for _folder in self.parent.list_folders:
            folder_key = os.path.basename(_folder)
            all_data[folder_key] = [self.parent.data_dictionary[folder_key][_key].data
                                    for _key in self.parent.data_dictionary[folder_key].keys()]

            self.parent.eventProgress.setValue(progress_index)
            progress_index += 1
            QtGui.QGuiApplication.processEvents()

        left_bin_index = 0
        for _folder in self.parent.list_folders:
            folder_key = os.path.basename(_folder)
            all_data_of_folder = all_data[folder_key]
            list_mean_counts_of_bin = []
            while left_bin_index < len(list_bin)-1:
                data_bin = all_data_of_folder[list_bin[left_bin_index]:list_bin[left_bin_index+1]]
                mean_data_bin = np.nanmean(data_bin, axis=0)
                list_mean_counts_of_bin.append(mean_data_bin)
                left_bin_index += 1

            self.parent.eventProgress.setValue(progress_index)
            progress_index += 1
            QtGui.QGuiApplication.processEvents()

        self.parent.eventProgress.setVisible(False)
        self.parent.ui.statusbar.showMessage("Done calculating the best contrast images!", 10000)
        QApplication.restoreOverrideCursor()
