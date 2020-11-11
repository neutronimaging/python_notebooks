import os
import numpy as np
from qtpy.QtWidgets import QComboBox

from __code._utilities.table_handler import TableHandler


class CoarseTableHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def initialize_table(self):
        list_folders = self.parent.list_folders
        short_list_folders = [''] + [os.path.basename(_file) for _file in list_folders]

        nbr_folders = len(list_folders)

        o_table = TableHandler(table_ui=self.parent.ui.coarse_alignment_tableWidget)

        nbr_row = nbr_column = nbr_folders
        for _row in np.arange(nbr_row):
            o_table.insert_empty_row(row=_row)
            for _col in np.arange(nbr_column):
                if _row == 0:
                    o_table.insert_empty_column(_col)
                _widget = QComboBox()
                _widget.addItems(short_list_folders)
                _widget.currentIndexChanged.connect(self.parent.coarse_alignment_table_combobox_changed)
                o_table.insert_widget(row=_row, column=_col, widget=_widget)

        column_width = [200 for _ in np.arange(nbr_column)]
        row_height = [40 for _ in np.arange(nbr_row)]
        o_table.set_column_sizes(column_sizes=column_width)
        o_table.set_row_height(row_height=row_height)
