import glob
from collections import OrderedDict
import os
import json
from qtpy import QtGui

from NeuNorm.normalization import Normalization

THIS_FILE_PATH = os.path.dirname(__file__)
CONFIG_FILE = os.path.join(THIS_FILE_PATH, 'config.json')


class MetadataData:
    """
    object that will store the data (2D array) of each image and metadata
    """
    data = None
    metadata = None

    def keep_only_metadata_defined_in_config(self, list_key=None):
        metadata_to_keep = {}
        for key in list_key:
            metadata_to_keep[key] = self.metadata[key]
        self.metadata = metadata_to_keep


class LoadData:

    master_dictionary = None
    metadata_key_to_keep = None

    def __init__(self, parent=None, list_folders=None):
        self.parent = parent
        self.list_folders = list_folders
        self.load_config()

    def load_config(self):
        with open(CONFIG_FILE) as f:
            config = json.load(f)

        self.metadata_key_to_keep = []
        for key in config.keys():
            self.metadata_key_to_keep.append(config[key]['key'])

    def run(self):
        nbr_folder = len(self.list_folders)
        self.parent.eventProgress.setMaximum(nbr_folder)
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)

        master_dict = OrderedDict()
        for _folder_index, _folder in enumerate(self.list_folders):
            o_norm = Normalization()
            list_files = glob.glob(_folder + "/*.tiff")
            o_norm.load(file=list_files, notebook=False)

            local_dict = OrderedDict()
            for _index, _file in enumerate(list_files):
                _metadatadata = MetadataData()
                _metadatadata.data = o_norm.data['sample']['data'][_index]
                _metadatadata.metadata = o_norm.data['sample']['metadata'][_index]
                _metadatadata.keep_only_metadata_defined_in_config(list_key=self.metadata_key_to_keep)
                local_dict[_file] = _metadatadata

            master_dict[os.path.basename(_folder)] = local_dict
            self.parent.eventProgress.setValue(_folder_index+1)
            QtGui.QGuiApplication.processEvents()

        self.parent.data_dictionary = master_dict
        self.parent.eventProgress.setVisible(False)
