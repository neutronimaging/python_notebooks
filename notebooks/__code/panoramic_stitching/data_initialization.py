from collections import OrderedDict
import copy
import numpy as np
import json
import os

THIS_FILE_PATH = os.path.dirname(__file__)
CONFIG_FILE = os.path.join(THIS_FILE_PATH, 'config.json')

X_METADATA_NAME = 'MotLongAxis.RBV'
Y_METADATA_NAME = 'MotLiftTable.RBV'


class DataInitialization:

    def __init__(self, parent=None):
        self.parent = parent

    def offset_table(self):
        data_dictionary = self.parent.data_dictionary
        offset_dictionary = OrderedDict()
        _offset_dict = None

        image_width, image_height = self._get_image_size()

        for _folder_name in data_dictionary.keys():
            xoffset = 0
            yoffset = 0
            _dict = OrderedDict()
            previous_metadata = {}
            for _file_index, _file in enumerate(data_dictionary[_folder_name].keys()):

                current_metadata = data_dictionary[_folder_name][_file].metadata

                if _file_index == 0:
                    xoffset = 0
                    yoffset = 0
                else:
                    if current_metadata[X_METADATA_NAME] < previous_metadata[X_METADATA_NAME]:
                        xoffset = 0
                        yoffset += image_height
                    else:
                        xoffset += image_width
                previous_metadata = copy.deepcopy(current_metadata)

                _offset_dict = {'xoffset': xoffset,
                                'yoffset': yoffset,
                                'visible': True}

                _dict[_file] = _offset_dict

            offset_dictionary[_folder_name] = _dict
        self.parent.offset_dictionary = offset_dictionary

    def _get_image_size(self):
        data_dictionary = self.parent.data_dictionary
        for _key_folder in data_dictionary.keys():
            for _key_file in data_dictionary[_key_folder].keys():
                data = data_dictionary[_key_folder][_key_file].data
                return np.shape(data)

    def _get_config(self):
        with open(CONFIG_FILE) as f:
            config = json.load(f)
        return config
