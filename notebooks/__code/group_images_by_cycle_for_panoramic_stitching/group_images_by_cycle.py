from collections import OrderedDict

from __code.metadata_handler import MetadataHandler


class GroupImagesByCycle:

    def __init__(self, list_of_files=None, list_of_metadata_key=None):
        """

        :param list_of_files: [file1, file2, file3, ...]
        :param list_of_metadata_key: [65024, 65034, ... ]
        """
        self.list_of_files = list_of_files
        self.list_of_metadata_key = list_of_metadata_key

        self.master_dictionary = None

    def create_master_dictionary(self):
        master_dictionary = MetadataHandler.retrieve_value_of_metadata_key(list_files=self.list_of_files,
                                                                           list_key=self.list_of_metadata_key)

        clean_master_dictionary = OrderedDict()
        for _file in master_dictionary.keys():
            _file_dict = master_dictionary[_file]
            _clean_file_dict = {}
            for _key in _file_dict.keys():
                _element = _file_dict[_key]
                _name, _value = _element.split(":")
                _clean_file_dict[_name] = _value
            clean_master_dictionary[_file] = _clean_file_dict

        self.master_dictionary = clean_master_dictionary
