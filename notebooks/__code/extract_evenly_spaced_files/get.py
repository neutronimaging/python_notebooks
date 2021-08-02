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
        array_of_indexes = np.arange(1, nbr_files, extracting_value)

        list_of_files_to_extract = []
        for _index in array_of_indexes:
            list_of_files_to_extract.append(list_of_files[_index])

        return list_of_files_to_extract

    def renamed_basename_list_of_files(self):
        list_of_files_to_extract = self.parent.basename_list_of_files_that_will_be_extracted

        renamed_list_of_files_to_extract = []
        for _counter, _file in enumerate(list_of_files_to_extract):
            [_name, ext] = os.path.splitext(_file)
            _name_split = _name.split('_')
            new_name = "_".join(_name_split[:-1]) + "_{:04d}{}".format(_counter, ext)
            renamed_list_of_files_to_extract.append(new_name)
        return renamed_list_of_files_to_extract
