from __code.normalization import LOG_FILENAME
from __code._utilities.get import Get as TopGet

from __code.normalization import LOG_FILENAME
from __code import file_handler


class Get(TopGet):

    def log_file_name(self):
        return TopGet.log_file_name(LOG_FILENAME)

    @staticmethod
    def list_of_tiff_files(folder=""):
        list_of_tiff_files = file_handler.get_list_of_files(folder=folder,
                                                            extension='tiff')
        return list_of_tiff_files
