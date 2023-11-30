from qtpy.QtWidgets import QMenu
from qtpy import QtGui
import numpy as np

from __code._utilities.table_handler import TableHandler
from __code._utilities.check import is_float


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def table_right_click(self):

        top_menu = QMenu(self.parent)

        state_of_paste = True
        if self.parent.value_to_copy is None:
            state_of_paste = False

        copy_menu = QMenu("Copy ...")
        top_menu.addMenu(copy_menu)
        copy_xoffset_menu = copy_menu.addAction("From first xoffset cell selected")
        copy_yoffset_menu = copy_menu.addAction("From first yoffset cell selected")

        paste_menu = QMenu("Paste ...")
        paste_menu.setEnabled(state_of_paste)
        top_menu.addMenu(paste_menu)
        paste_xoffset_menu = paste_menu.addAction("In all xoffset cell selected")
        paste_yoffset_menu = paste_menu.addAction("In all yoffset cell selected")

        action = top_menu.exec_(QtGui.QCursor.pos())

        if action == copy_xoffset_menu:
            self.copy_xoffset_value()
        elif action == copy_yoffset_menu:
            self.copy_yoffset_value()
        elif action == paste_xoffset_menu:
            self.paste_xoffset_value()
        elif action == paste_yoffset_menu:
            self.paste_yoffset_value()

    def copy_xoffset_value(self):
        self.parent.value_to_copy = self.get_value_to_copy(column=1)

    def copy_yoffset_value(self):
        self.parent.value_to_copy = self.get_value_to_copy(column=2)

    def get_value_to_copy(self, column=1):
        o_table = TableHandler(self.parent.ui.tableWidget)
        row_selected = o_table.get_row_selected()
        value_to_copy = o_table.get_item_str_from_cell(row=row_selected,
                                                       column=column)
        return value_to_copy

    def paste_xoffset_value(self):
        self.paste_value_copied(column=1)

    def paste_yoffset_value(self):
        self.paste_value_copied(column=2)

    def paste_value_copied(self, column=1):
        o_table = TableHandler(self.parent.ui.tableWidget)
        row_selected = o_table.get_rows_of_table_selected()
        self.parent.ui.tableWidget.blockSignals(True)

        for _row in row_selected:
            o_table.set_item_with_str(row=_row,
                                      column=column,
                                      cell_str=self.parent.value_to_copy)

        self.parent.ui.tableWidget.blockSignals(False)

    def update_table_according_to_filter(self):
        filter_flag = self.parent.ui.filter_radioButton.isChecked()
    
        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
    
        def should_row_be_visible(row_value=None, filter_algo_selected="<=", filter_value=None):
    
            if is_float(filter_value):
                o_table.set_all_row_hidden(False)
                return
    
            if filter_algo_selected == "<=":
                return float(row_value) <= float(filter_value)
            elif filter_algo_selected == ">=":
                return float(row_value) >= float(filter_value)
            else:
                raise NotImplementedError("algo not implemented!")
    
        if filter_flag:
            # select only rows according to filter
            filter_column_selected = self.parent.ui.filter_column_name_comboBox.currentText()
            filter_algo_selected = self.parent.ui.filter_logic_comboBox.currentText()
            filter_value = self.parent.ui.filter_value.text()
    
            if filter_column_selected == "Xoffset":
                filter_column_index = 1
            elif filter_column_selected == "Yoffset":
                filter_column_index = 2
            elif filter_column_selected == "Rotation":
                filter_column_index = 3
            else:
                raise NotImplementedError("column can not be used with filter!")
    
            nbr_row = o_table.row_count()
            for _row in np.arange(nbr_row):
                _row_value = float(o_table.get_item_str_from_cell(row=_row, column=filter_column_index))
                _should_row_be_visible = should_row_be_visible(row_value=_row_value,
                                                               filter_algo_selected=filter_algo_selected,
                                                               filter_value=filter_value)
                o_table.set_row_hidden(_row, not _should_row_be_visible)
        else:
            # all rows are visible
            o_table.set_all_row_hidden(False)

    def close_all_markers(self):
        for marker in self.parent.markers_table.keys():
            self.close_markers_of_tab(marker_name=marker)

    def close_markers_of_tab(self, marker_name=''):
        """remove box and label (if they are there) of each marker"""
        _data = self.parent.markers_table[marker_name]['data']
        for _file in _data:
            _marker_ui = _data[_file]['marker_ui']
            if _marker_ui:
                self.parent.ui.image_view.removeItem(_marker_ui)

            _label_ui = _data[_file]['label_ui']
            if _label_ui:
                self.parent.ui.image_view.removeItem(_label_ui)
