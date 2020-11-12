from collections import OrderedDict
import copy
import numpy as np
import os

from __code._utilities.table_handler import TableHandler
from __code.panoramic_stitching_for_tof.coarse_tab_handler import CoarseTabHandler

X_METADATA_NAME = 'MotLongAxis.RBV'
Y_METADATA_NAME = 'MotLiftTable.RBV'


class DataInitialization:

    def __init__(self, parent=None):
        self.parent = parent

    def offset_table(self):
        offset_dictionary = OrderedDict()
        image_width = self.parent.image_width
        image_height = self.parent.image_height

        o_table = TableHandler(table_ui=self.parent.ui.coarse_alignment_tableWidget)

        list_folders = self.parent.list_folders
        # short_list_folders = [''] + [os.path.basename(_file) for _file in list_folders]
        nbr_folders = len(list_folders)

        o_coarse = CoarseTabHandler(parent=self.parent)
        nbr_row = self.parent.ui.coarse_alignment_tableWidget.rowCount()
        nbr_column = self.parent.ui.coarse_alignment_tableWidget.columnCount()
        nbr_empty_rows = o_coarse.get_number_of_empty_rows_from_top(nbr_row=nbr_row, nbr_column=nbr_column)
        nbr_empty_columns = o_coarse.get_number_of_empty_columns_from_left(nbr_row=nbr_row, nbr_column=nbr_column)

        nbr_row = nbr_column = nbr_folders
        for _row in np.arange(nbr_row):
            for _column in np.arange(nbr_column):
                _widget = o_table.get_widget(row=_row, column=_column)
                folder_name = _widget.currentText()
                if not folder_name == "":
                    xoffset = (_column - nbr_empty_columns) * image_width
                    yoffset = (_row - nbr_empty_rows) * image_height
                    _offset_dict = {'xoffset': xoffset,
                                    'yoffset': yoffset,
                                    'visible': True}
                    offset_dictionary[folder_name] = _offset_dict

        self.parent.offset_dictionary = offset_dictionary
        self.parent.offset_dictionary_for_reset = copy.deepcopy(offset_dictionary)

    def _get_image_size(self):
        data_dictionary = self.parent.data_dictionary
        for _key_folder in data_dictionary.keys():
            for _key_file in data_dictionary[_key_folder].keys():
                data = data_dictionary[_key_folder][_key_file].data
                return np.shape(data)
