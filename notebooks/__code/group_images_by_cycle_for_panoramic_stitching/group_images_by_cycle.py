from collections import OrderedDict
import numpy as np

from __code.metadata_handler import MetadataHandler
from __code._utilities.list import are_those_two_list_identical_within_tolerance


class GroupImagesByCycle:

    def __init__(self, list_of_files=None, list_of_metadata_key=None, tolerance_value=0.1):
        """

        :param list_of_files: [file1, file2, file3, ...]
        :param list_of_metadata_key: [65024, 65034, ... ]
        """
        self.list_of_files = list_of_files
        self.list_of_metadata_key_value_number = list_of_metadata_key
        self.tolerance_value = tolerance_value

        self.master_dictionary = None
        self.list_of_metadata_key_real_name = None
        self.dictionary_of_groups = OrderedDict()

    def run(self):
        self.create_master_dictionary()
        self.group()

    def create_master_dictionary(self):
        master_dictionary = MetadataHandler.retrieve_value_of_metadata_key(list_files=self.list_of_files,
                                                                           list_key=self.list_of_metadata_key_value_number)

        clean_master_dictionary = OrderedDict()
        list_metadata_key = []
        for _index, _file in enumerate(master_dictionary.keys()):
            _file_dict = master_dictionary[_file]
            _clean_file_dict = {}
            for _key in _file_dict.keys():
                _element = _file_dict[_key]
                _name, _value = _element.split(":")
                if _index == 0:
                    list_metadata_key.append(_name)
                _clean_file_dict[_name] = _value
            clean_master_dictionary[_file] = _clean_file_dict

        self.master_dictionary = clean_master_dictionary
        self.list_of_metadata_key_real_name = list_metadata_key

    def group(self):
        master_dictionary = self.master_dictionary
        group_index = 0
        list_files_in_that_group = []

        full_list_of_metadata_list = list()
        for _file in master_dictionary.keys():
            _file_dictionary = master_dictionary[_file]

            # loop through the metadata of each file
            list_of_metadata_for_that_file = list()
            for _key in _file_dictionary.keys():
                _value = np.float(_file_dictionary[_key])
                list_of_metadata_for_that_file.append(_value)

            if not are_those_two_list_identical_within_tolerance(list_of_metadata_for_that_file,
                                                                 full_list_of_metadata_list,
                                                                 tolerance=self.tolerance_value):
                full_list_of_metadata_list.append(list_of_metadata_for_that_file)
                list_files_in_that_group.append(_file)
            else:
                self.dictionary_of_groups[group_index] = list_files_in_that_group
                list_files_in_that_group = [_file]
                full_list_of_metadata_list = list()
                group_index += 1

        self.dictionary_of_groups[group_index] = list_files_in_that_group

