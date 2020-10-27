from collections import OrderedDict
import copy


class DataInitialization:

    def __init__(self, parent=None):
        self.parent = parent

    def offset_table(self):
        data_dictionary = self.parent.data_dictionary
        offset_dictionary = OrderedDict()
        _offset_dict = {'xoffset': 0, 'yoffset': 0}

        for _folder_name in data_dictionary.keys():
            _dict = OrderedDict()
            for _file in data_dictionary[_folder_name].keys():
                _dict[_file] = copy.deepcopy(_offset_dict)
            offset_dictionary[_folder_name] = _dict
        self.parent.offset_dictionary = offset_dictionary
