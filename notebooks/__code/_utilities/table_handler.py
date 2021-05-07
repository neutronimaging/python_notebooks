import numpy as np
from qtpy import QtGui, QtCore
from qtpy.QtWidgets import QTableWidgetItem, QTableWidgetSelectionRange

from __code._utilities.widgets_handler import WidgetsHandler


class TableHandler:
    cell_str_format = "{:.3f}"
    cell_str_format = "{}"

    def __init__(self, table_ui=None):
        self.table_ui = table_ui

    def select_everything(self, state):
        nbr_row = self.table_ui.rowCount()
        nbr_column = self.table_ui.columnCount()
        selection_range = QTableWidgetSelectionRange(0, 0, nbr_row - 1, nbr_column - 1)
        self.table_ui.setRangeSelected(selection_range, state)

    def row_count(self):
        return self.table_ui.rowCount()

    def column_count(self):
        return self.table_ui.columnCount()

    def select_rows(self, list_of_rows=None):
        self.table_ui.blockSignals(True)
        self.select_everything(False)
        nbr_row = self.table_ui.rowCount()
        nbr_column = self.table_ui.columnCount()

        for _row in list_of_rows:
            selection_range = QTableWidgetSelectionRange(_row, 0, _row, nbr_column - 1)
            self.table_ui.setRangeSelected(selection_range, True)
        self.table_ui.blockSignals(False)

    def remove_all_rows(self):
        nbr_row = self.table_ui.rowCount()
        for _ in np.arange(nbr_row):
            self.table_ui.removeRow(0)

    def remove_all_columns(self):
        nbr_column = self.table_ui.columnCount()
        for _ in np.arange(nbr_column):
            self.table_ui.removeColumn(0)

    def full_reset(self):
        self.remove_all_rows()
        self.remove_all_columns()

    def get_rows_of_table_selected(self):
        if self.table_ui is None:
            return None

        selected_ranges = self.table_ui.selectedRanges()
        if selected_ranges == []:
            return None

        list_row_selected = []
        for _selection in selected_ranges:
            top_row = _selection.topRow()
            bottom_row = _selection.bottomRow()
            if top_row == bottom_row:
                list_row_selected.append(top_row)
            else:
                _range = np.arange(top_row, bottom_row + 1)
                for _row in _range:
                    list_row_selected.append(_row)

        return list_row_selected

    def get_row_selected(self):
        if self.table_ui is None:
            return -1
        list_selection = self.table_ui.selectedRanges()
        try:
            first_selection = list_selection[0]
        except IndexError:
            return -1
        return first_selection.topRow()

    def get_cell_selected(self):
        list_selection = self.table_ui.selectedRanges()
        first_selection = list_selection[0]
        row = first_selection.topRow()
        col = first_selection.leftColumn()
        return row, col

    def get_item_str_from_cell(self, row=-1, column=-1):
        item_selected = self.table_ui.item(row, column).text()
        return str(item_selected)

    def select_cell(self, row=0, column=0):
        self.select_everything(False)
        range_selected = QTableWidgetSelectionRange(row, column, row, column)
        self.table_ui.setRangeSelected(range_selected, True)

    def select_row(self, row=0):
        if row < 0:
            row = 0
        self.table_ui.selectRow(row)

    def set_column_names(self, column_names=None):
        self.table_ui.setHorizontalHeaderLabels(column_names)

    def set_row_names(self, row_names=None):
        self.table_ui.setVerticalHeaderLabels(row_names)

    def set_column_sizes(self, column_sizes=None):
        for _col, _size in enumerate(column_sizes):
            self.table_ui.setColumnWidth(_col, _size)

    def set_column_width(self, column_width=None):
        self.set_column_sizes(column_sizes=column_width)

    def set_row_height(self, row_height=None):
        for _row, _height in enumerate(row_height):
            self.table_ui.setRowHeight(_row, _height)

    def insert_empty_row(self, row=0):
        self.table_ui.insertRow(row)

    def insert_row(self, row=0, list_col_name=None):
        """row is the row number
        """
        self.table_ui.insertRow(row)
        for column, _text in enumerate(list_col_name):
            _item = QTableWidgetItem(_text)
            self.table_ui.setItem(row, column, _item)

    def is_item(self, row=0, column=0):
        if self.table_ui.item(row, column):
            return True
        return False

    def get_widget(self, row=-1, column=-1):
        _widget = self.table_ui.cellWidget(row, column)
        return _widget

    def insert_column(self, column):
        self.table_ui.insertColumn(column)

    def insert_empty_column(self, column):
        self.insert_column(column)

    def set_item_with_str(self, row=0, column=0, cell_str=""):
        self.table_ui.item(row, column).setText(cell_str)

    def set_item_with_float(self, row=0, column=0, float_value=""):
        if (str(float_value) == 'None') or (str(float_value) == 'N/A'):
            _str_value = "N/A"
        else:
            _str_value = self.cell_str_format.format(np.float(float_value))
        self.table_ui.item(row, column).setText(_str_value)

    def insert_item_with_float(self, row=0, column=0, float_value="", format_str="{}"):
        if (str(float_value) == 'None') or (str(float_value) == 'N/A'):
            _str_value = "N/A"
        else:
            _str_value = format_str.format(np.float(float_value))
        _item = QTableWidgetItem(_str_value)
        self.table_ui.setItem(row, column, _item)

    def insert_item(self, row=0, column=0, value="", format_str="{}", editable=True):
        _str_value = format_str.format(value)
        _item = QTableWidgetItem(_str_value)
        if not editable:
            _item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        self.table_ui.setItem(row, column, _item)

    def insert_widget(self, row=0, column=0, widget=None):
        self.table_ui.setCellWidget(row, column, widget)

    def set_background_color(self, row=0, column=0, qcolor=QtGui.QColor(0, 255, 255)):
        _item = self.table_ui.item(row, column)
        _item.setBackground(qcolor)

    def fill_table_with(self, list_items=None, editable_columns_boolean=None, block_signal=False):
        """
        :param:
        list_items: 2D array of text to put in the table
            ex: list_items = [ ['file1', 10, 20'], ['file2', 20, 30] ...]
        editable_columns_boolean: which columns are editable
            ex: editable_columns_boolean = [False, True, True]
        block_signals: block or not any signal emitted by the table
        """
        if block_signal:
            WidgetsHandler.block_signals(ui=self.table_ui,
                                         status=True)

        self.remove_all_rows()

        for _row_index, _row_entry in enumerate(list_items):
            self.insert_empty_row(_row_index)
            for _column_index, _text in enumerate(list_items[_row_index]):
                if _row_index == 0:
                    editable_flag = False
                else:
                    editable_flag = editable_columns_boolean[_column_index]
                self.insert_item(row=_row_index,
                                 column=_column_index,
                                 value=_text,
                                 editable=editable_flag)

        if block_signal:
            WidgetsHandler.block_signals(ui=self.table_ui,
                                         status=False)
