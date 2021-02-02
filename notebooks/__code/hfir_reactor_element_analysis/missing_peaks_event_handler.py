from qtpy.QtWidgets import QMenu
from qtpy import QtGui

from __code._utilities.table_handler import TableHandler


class MissingPeaksEventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def right_click(self):

        o_table = TableHandler(table_ui=self.parent.ui.missing_peaks_tableWidget)
        row, col = o_table.get_cell_selected()

        list_of_images = self.parent.list_of_images

        file_name_value = list_of_images[row]
        angle_value = self.parent.list_ideal_position_of_elements[col]

        menu = QMenu(self.parent)

        file_name = menu.addAction("file name: {}".format(file_name_value))
        angle = menu.addAction("angle: {}".format(angle_value))

        action = menu.exec_(QtGui.QCursor.pos())
