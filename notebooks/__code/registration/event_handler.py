from qtpy.QtWidgets import QMenu
from qtpy import QtGui

from __code._utilities.table_handler import TableHandler


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
