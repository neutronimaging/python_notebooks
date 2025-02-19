import numpy as np
import os
import re
from qtpy.QtWidgets import QMainWindow
from qtpy import QtGui, QtCore

from __code import load_ui
from __code.metadata_overlapping_images import HELP_PAGE, LIST_FUNNY_CHARACTERS


class MetadataStringFormatLauncher:

    def __init__(self, parent=None):
        self.parent = parent

        if self.parent.metadata_string_format_ui is None:
            metadata_string_format_ui = MetadataStringFormatHandler(parent=parent)
            metadata_string_format_ui.show()
            self.parent.metadata_string_format_ui = metadata_string_format_ui
        else:
            self.parent.metadata_string_format_ui.setFocus()
            self.parent.metadata_string_format_ui.activateWindow()


class MetadataStringFormatHandler(QMainWindow):

    column_width = [400, 100]

    def __init__(self, parent=None):

        self.parent = parent
        super(MetadataStringFormatHandler, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui', 'ui_metadata_overlapping_images_string_format.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Clean String")

        self.init_table()
        self.init_table_size()

    def set_item_parent_table(self, row=0, col=0, value='', editable=False):
        item = QtGui.QTableWidgetItem(str(value))
        self.parent.ui.tableWidget.setItem(row, col, item)
        if not editable:
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

    def ok(self):
        nbr_row = self.ui.tableWidget.rowCount()
        for _row in np.arange(nbr_row):
            _row_str = str(self.ui.tableWidget.item(_row, 1).text())
            self.set_item_parent_table(row=_row, col=1, value=_row_str, editable=True)
        self.cancel()

    def cancel(self):
        self.parent.metadata_string_format_ui = None
        self.close()

    def launch_help(self):
        import webbrowser
        webbrowser.open(HELP_PAGE)

    def string_format_changed(self, value):
        _first_part = self.ui.first_part_lineEdit.text()
        _clean_first_part = ""
        for _c in _first_part:
            if _c in LIST_FUNNY_CHARACTERS:
                _clean_first_part += "\{}".format(_c)
            else:
                _clean_first_part += "{}".format(_c)

        _second_part = self.ui.second_part_lineEdit.text()
        _clean_second_part = ""
        for _c in _second_part:
            if _c in LIST_FUNNY_CHARACTERS:
                _clean_second_part += "\{}".format(_c)
            else:
                _clean_second_part += "{}".format(_c)

        regular_expr = r"{}(.*){}".format(_clean_first_part, _clean_second_part)

        nbr_row = self.ui.tableWidget.rowCount()
        for _row in np.arange(nbr_row):
            _row_str = str(self.parent.ui.tableWidget.item(_row, 1).text())
            m = re.match(regular_expr, _row_str)
            if m and m.group(1):
                _new_str = m.group(1)
                item = QtGui.QTableWidgetItem(_new_str)
                self.ui.tableWidget.setItem(_row, 1, item)

    def init_table_size(self):
        for _col_index, _col_width in enumerate(self.column_width):
            self.ui.tableWidget.setColumnWidth(_col_index, _col_width)

    def init_table(self):
        list_files_full_name = self.parent.data_dict['file_name']
        list_files_short_name = [os.path.basename(_file) for _file in list_files_full_name]

        main_table_metadata_column = self.parent.get_raw_metadata_column()

        for _row, _file in enumerate(list_files_short_name):
            self.ui.tableWidget.insertRow(_row)
            self.set_item_table(row=_row, col=0, value=_file)
            self.set_item_table(row=_row, col=1, value=main_table_metadata_column[_row], editable=True)

    def set_item_table(self, row=0, col=0, value='', editable=False):
        item = QtGui.QTableWidgetItem(str(value))
        self.ui.tableWidget.setItem(row, col, item)
        if not editable:
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
