import numpy as np
import os

from __code._utilities.get import Get as TopGet

from __code.extract_evenly_spaced_files import LOG_FILENAME


class Get(TopGet):

    def log_file_name(self):
        return TopGet.log_file_name(LOG_FILENAME)

    def number_of_files_to_extract(self):
        extracting_value = self.parent.extracting_ui.value
        nbr_files = self.parent.number_of_files
        return int(nbr_files / extracting_value)

    def list_of_files_to_extract(self):
        extracting_value = self.parent.extracting_ui.value
        list_of_files = self.parent.list_files
        nbr_files = self.parent.number_of_files
        array_of_indexes = np.arange(0, nbr_files, extracting_value)

        list_of_files_to_extract = []
        for _index in array_of_indexes:
            list_of_files_to_extract.append(list_of_files[_index])

        return list_of_files_to_extract

    def renamed_basename_list_of_files(self, prefix):
        list_of_files_to_extract = self.parent.basename_list_of_files_that_will_be_extracted
        if prefix:
            prefix += "_"

        renamed_list_of_files_to_extract = []
        for _counter, _file in enumerate(list_of_files_to_extract):
            [_name, ext] = os.path.splitext(_file)
            new_name = prefix + "{:04d}{}".format(_counter, ext)
            renamed_list_of_files_to_extract.append(new_name)
        return renamed_list_of_files_to_extract

    def index_of_file_selected_in_full_list(self, base_file_name):
        return self.parent.full_base_list_of_files.index(base_file_name)
