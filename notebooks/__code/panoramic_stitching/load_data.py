import glob
from collections import OrderedDict
import os

from NeuNorm.normalization import Normalization


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
                local_dict[_file] = _metadatadata

            master_dict[os.path.basename(_folder)] = local_dict
            self.parent.eventProgress.setValue(_folder_index+1)

        self.parent.data_dictionary = master_dict
        self.parent.eventProgress.setVisible(False)
