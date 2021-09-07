import os
import numpy as np
from qtpy.QtWidgets import QComboBox

from __code._utilities.table_handler import TableHandler


class CoarseTabHandler:

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

    def combobox_changed(self):
        # list_folders = self.parent.list_folders
        # nbr_folders = len(list_folders)

        nbr_row = self.parent.ui.coarse_alignment_tableWidget.rowCount()
        nbr_column = self.parent.ui.coarse_alignment_tableWidget.columnCount()

        data_dictionary = self.parent.coarse_images_dictionary
        image_width = self.parent.image_width
        image_height = self.parent.image_height

        o_table = TableHandler(table_ui=self.parent.ui.coarse_alignment_tableWidget)
        panoramic_width = 0
        panoramic_height = 0
        for _row in np.arange(nbr_row):
            width = 0
            height = 0
            for _column in np.arange(nbr_column):
                _widget = o_table.get_widget(row=_row, column=_column)
                folder_name = _widget.currentText()
                if not folder_name == "":
                    width = (_column + 1) * image_width
                    height = (_row + 1) * image_height

            if width > panoramic_width:
                panoramic_width = width
            if height > panoramic_height:
                panoramic_height = height

        # number of empty rows and columns before first file selected
        nbr_empty_rows = self.get_number_of_empty_rows_from_top(nbr_row=nbr_row, nbr_column=nbr_column)
        nbr_empty_columns = self.get_number_of_empty_columns_from_left(nbr_row=nbr_row, nbr_column=nbr_column)

        panoramic_image = np.zeros((panoramic_height, panoramic_width))
        for _row in np.arange(nbr_row):
            for _column in np.arange(nbr_column):
                _widget = o_table.get_widget(row=_row, column=_column)
                folder_name = _widget.currentText()
                if not folder_name == "":
                    data = data_dictionary[folder_name].data
                    real_row_nbr = _row - nbr_empty_rows
                    real_col_nbr = _column - nbr_empty_columns
                    panoramic_image[real_row_nbr*image_height:(real_row_nbr+1)*image_height,
                                    real_col_nbr*image_width:(real_col_nbr+1)*image_width] = data

        self.parent.coarse_panoramic_image = panoramic_image

    def get_number_of_empty_rows_from_top(self, nbr_row=-1, nbr_column=-1):
        nbr_empty_row = 0
        o_table = TableHandler(table_ui=self.parent.ui.coarse_alignment_tableWidget)
        for _row in np.arange(nbr_row):
            for _column in np.arange(nbr_column):
                _widget = o_table.get_widget(row=_row, column=_column)
                folder_name = _widget.currentText()
                if not folder_name == "":
                    return nbr_empty_row
            nbr_empty_row += 1
        return nbr_empty_row

    def get_number_of_empty_columns_from_left(self, nbr_row=-1, nbr_column=-1):
        nbr_empty_column = 0
        o_table = TableHandler(table_ui=self.parent.ui.coarse_alignment_tableWidget)
        for _column in np.arange(nbr_column):
            for _row in np.arange(nbr_row):
                _widget = o_table.get_widget(row=_row, column=_column)
                folder_name = _widget.currentText()
                if not folder_name == "":
                    return nbr_empty_column
            nbr_empty_column += 1
        return nbr_empty_column

    def update_coarse_panoramic_image(self):
        _image = np.transpose(self.parent.coarse_panoramic_image)
        if len(_image) == 0:
            self.parent.ui.image_view_coarse_alignment.clear()
        else:
            self.parent.ui.image_view_coarse_alignment.setImage(_image)

