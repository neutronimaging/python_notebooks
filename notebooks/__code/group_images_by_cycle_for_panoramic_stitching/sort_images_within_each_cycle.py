from collections import OrderedDict
import pandas as pd


class SortImagesWithinEachCycle:

    dict_groups_filename_sorted = None

    def __init__(self, dict_groups_filename=None, dict_filename_metadata=None):
        """
        using sorting arguments, will create a dictionary of files sorted

        :param dict_groups_filename: {'file1': {'var1': value1, 'var2': value2},
                                      'file2': {'var1': value1, 'var2': value2},
                                       ... }
        :param dict_filename_metadata: {0: ['file1', 'file2', ...],
                                        1: ['file5', 'file6', ...],
                                        ... }
        """
        self.dict_groups_filename = dict_groups_filename
        self.dict_filename_metadata = dict_filename_metadata

    def sort(self, dict_how_to_sort=None):
        """
        This will sort each group according to the criteria defined in dict_how_to_sort

        :param dict_how_to_sort: {'1st_variable': {'name': 'MotLiftTable',
                                                   'is_ascending': True},
                                  '2nd_variable': {'name': 'MotLongAxis',
                                                   'is_ascending': False}
        """

        dict_groups_filename_sorted = OrderedDict()
        for _group_index in self.dict_groups_filename.keys():
            list_files = self.dict_groups_filename[_group_index]
            list_files_sorted = self.sort_files(list_files, dict_how_to_sort)
            dict_groups_filename_sorted[_group_index] = list_files_sorted
        self.dict_groups_filename_sorted = dict_groups_filename_sorted

    def sort_files(self, list_files=None, dict_how_to_sort=None):
        list_metadata = self.dict_filename_metadata[list_files[0]].keys()
        frames = []
        name_of_columns = ['filename']
        data = []
        for _index, _file in enumerate(list_files):
            _entry = [_file]
            for _key in list_metadata:
                if _index == 0:
                    name_of_columns.append(_key)
                _entry.append(float(self.dict_filename_metadata[_file][_key]))
            data.append(_entry)

        df = pd.DataFrame(data, columns=name_of_columns)
        frames.append(df)
        result = pd.concat(frames)

        new_result_sorted = result.sort_values(by=[dict_how_to_sort['1st_variable']['name'],
                                                   dict_how_to_sort['2nd_variable']['name']],
                                               ascending=[dict_how_to_sort['1st_variable']['is_ascending'],
                                                          dict_how_to_sort['2nd_variable']['is_ascending']])

        return list(new_result_sorted['filename'])
