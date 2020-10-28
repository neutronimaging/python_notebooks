import numpy as np

from __code._utilities.table_handler import TableHandler
from __code.panoramic_stitching.get import Get


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def save_table_offset_of_this_cell(self, row=-1, column=-1):
        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)

        offset_value = np.int(o_table.get_item_str_from_cell(row=row, column=column))
        file_name = o_table.get_item_str_from_cell(row=row, column=0)

        o_get = Get(parent=self.parent)
        folder_selected = o_get.get_combobox_folder_selected()

        offset_dictionary = self.parent.offset_dictionary
        offset_key_name = 'xoffset' if column == 1 else 'yoffset'

        offset_dictionary[folder_selected][file_name][offset_key_name] = offset_value
        self.parent.offset_dictionary = offset_dictionary
