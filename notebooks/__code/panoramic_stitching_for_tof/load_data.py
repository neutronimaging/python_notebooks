import glob
import os
from collections import OrderedDict

import numpy as np
from NeuNorm.normalization import Normalization
from qtpy import QtCore, QtGui
from qtpy.QtWidgets import QApplication

THIS_FILE_PATH = os.path.dirname(__file__)
CONFIG_FILE = os.path.join(THIS_FILE_PATH, "config_work.json")


class MetadataData:
    """
    object that will store the data (2D array) of each image and metadata
    """

    data = None
    metadata = None


class LoadData:
    master_dictionary = None

    def __init__(self, parent=None, list_folders=None):
        self.parent = parent
        self.list_folders = list_folders

    def run(self):
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        nbr_folder = len(self.list_folders)
        self.parent.eventProgress.setMaximum(nbr_folder)
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)

        master_dict = OrderedDict()
        integrated_images_dict = OrderedDict()
        for _folder_index, _folder in enumerate(self.list_folders):
            self.parent.ui.statusbar.showMessage(f"Loading data from folder {os.path.basename(_folder)}")
            QtGui.QGuiApplication.processEvents()

            o_norm = Normalization()
            list_files = glob.glob(_folder + "/*.tiff")
            list_files.sort()

            o_norm.load(file=list_files, notebook=False)

            # record size of images
            if _folder_index == 0:
                self.parent.image_height, self.parent.image_width = np.shape(o_norm.data["sample"]["data"][0])

            local_dict = OrderedDict()
            self.parent.nbr_files_per_folder = len(list_files)
            for _index, _file in enumerate(list_files):
                _metadatadata = MetadataData()
                _metadatadata.data = o_norm.data["sample"]["data"][_index]

                local_dict[_file] = _metadatadata

            master_dict[os.path.basename(_folder)] = local_dict

            o_data = MetadataData()
            _data = LoadData.calculate_integrated_data(o_norm.data["sample"]["data"])
            o_data.data = _data
            integrated_images_dict[os.path.basename(_folder)] = o_data

            self.parent.eventProgress.setValue(_folder_index + 1)
            QtGui.QGuiApplication.processEvents()

        self.parent.working_dir = os.path.dirname(self.list_folders[0])
        self.parent.integrated_images = integrated_images_dict
        self.parent.data_dictionary = master_dict
        self.parent.eventProgress.setVisible(False)

        coarse_images_dictionary = OrderedDict()
        for _folder in self.parent.integrated_images.keys():
            coarse_images_dictionary[os.path.basename(_folder)] = self.parent.integrated_images[_folder]
        self.parent.coarse_images_dictionary = coarse_images_dictionary

        self.parent.ui.statusbar.showMessage(f"Done Loading data from {nbr_folder} folders!", 5000)
        QApplication.restoreOverrideCursor()

    @staticmethod
    def calculate_integrated_data(list_arrays=None):
        return np.sum(list_arrays, 0, dtype=int16)
