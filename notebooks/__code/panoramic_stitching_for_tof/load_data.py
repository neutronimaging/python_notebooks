import glob
from collections import OrderedDict
import os
from qtpy import QtGui, QtCore
from qtpy.QtWidgets import QApplication
import numpy as np

from NeuNorm.normalization import Normalization

THIS_FILE_PATH = os.path.dirname(__file__)
CONFIG_FILE = os.path.join(THIS_FILE_PATH, 'config.json')


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

            self.parent.ui.statusbar.showMessage("Loading data from folder {}".format(os.path.basename(_folder)))
            QtGui.QGuiApplication.processEvents()

            o_norm = Normalization()
            list_files = glob.glob(_folder + "/*.tiff")
            list_files.sort()

            o_norm.load(file=list_files, notebook=False)

            # record size of images
            if _folder_index == 0:
                self.parent.image_height, self.parent.image_width = np.shape(o_norm.data['sample']['data'][0])

            local_dict = OrderedDict()
            for _index, _file in enumerate(list_files):
                _metadatadata = MetadataData()
                _metadatadata.data = o_norm.data['sample']['data'][_index]

                local_dict[_file] = _metadatadata

            master_dict[os.path.basename(_folder)] = local_dict

            o_data = MetadataData()
            _data = LoadData.calculate_integrated_data(o_norm.data['sample']['data'])
            o_data.data = _data
            integrated_images_dict[_folder] = o_data

            self.parent.eventProgress.setValue(_folder_index+1)
            QtGui.QGuiApplication.processEvents()

        self.parent.working_dir = os.path.dirname(self.list_folders[0])
        self.parent.integrated_images = integrated_images_dict
        self.parent.data_dictionary = master_dict
        self.parent.eventProgress.setVisible(False)

        self.parent.ui.statusbar.showMessage("Done Loading data from {} folders!".format(nbr_folder), 5000)
        QApplication.restoreOverrideCursor()

    @staticmethod
    def calculate_integrated_data(list_arrays=None):
        return np.sum(list_arrays, 0, dtype=np.int16)
