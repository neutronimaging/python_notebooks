import os
import numpy as np

from __code._utilities.table_handler import TableHandler


class Get:

    def __init__(self, parent=None):
        self.parent = parent

    def get_combobox_folder_selected(self):
        return os.path.basename(self.parent.ui.list_folders_combobox.currentText())

    def get_combobox_full_name_folder_selected(self):
        return self.parent.ui.list_folders_combobox.currentText()

    def get_list_folders_according_to_offset_table(self):
        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        nbr_row = o_table.table_ui.rowCount()
        list_folders = []
        for _row in np.arange(nbr_row):
            _folder = o_table.get_item_str_from_cell(row=_row, column=0)
            list_folders.append(_folder)
        return list_folders
