from collections import OrderedDict

from __code.metadata_handler import MetadataHandler
from __code._utilities.list import is_this_list_already_in_those_lists_within_tolerance


class GroupImagesByCycle:

    def __init__(self, list_of_files=None, list_of_metadata_key=None, tolerance_value=0.1):
        """

        :param list_of_files: [file1, file2, file3, ...]
        :param list_of_metadata_key: [65024, 65034, ... ]
        """
        self.list_of_files = list_of_files
        self.list_of_metadata_key_value_number = list_of_metadata_key
        self.tolerance_value = tolerance_value

        self.master_dictionary = OrderedDict()
        self.list_of_metadata_key_real_name = None
        self.dictionary_of_groups = OrderedDict()

    def run(self):
        self.create_master_dictionary()
        self.group()

    def create_master_dictionary(self):
        list_key_value = self.list_of_metadata_key_value_number
        master_dictionary = MetadataHandler.retrieve_value_of_metadata_key(list_files=self.list_of_files,
                                                                           list_key=list_key_value)

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
        """
        This will create a master dictionary such as
        dict = OrderedDict('value_outer_loop_1': {'value_inner_loop_1': ['file1'],
                                                  'value_inner_loop_2': ['file2', 'file3'],
                                                  'value_inner_loop_3': ['file4']},
                            'value_outer_loop_2': {'value_inner_loop_1': ['file5'],
                                                   'value_inner_loop_2': ['file6'],
                                                   ...,
                                                   },
        """
        master_dictionary = self.master_dictionary
        [outer_key, inner_key] = self.list_of_metadata_key_real_name

        list_of_outer_loop_values = []
        list_of_inner_loop_values = []

        # get list of outer loop values
        # get list of inner loop values
        for _file in master_dictionary.keys():
            _file_dictionary = master_dictionary[_file]

            outer_value = _file_dictionary[outer_key]
            inner_value = _file_dictionary[inner_key]

            list_of_outer_loop_values.append(outer_value)
            list_of_inner_loop_values.append(inner_value)

        # fill master dictionary
        master_grouped_dictionary = OrderedDict()
        for _file in master_dictionary.keys():
            _file_dictionary = master_dictionary[_file]
            outer_value = _file_dictionary[outer_key]
            inner_value = _file_dictionary[inner_key]

            if master_grouped_dictionary.get(outer_value, None) is None:
                master_grouped_dictionary[outer_value] = {inner_value: [_file]}

            elif master_grouped_dictionary[outer_value].get(inner_value, None) is None:
                master_grouped_dictionary[outer_value][inner_value] = [_file]

            else:
                master_grouped_dictionary[outer_value][inner_value].append(_file)

        self.master_outer_inner_dictionary = master_grouped_dictionary
