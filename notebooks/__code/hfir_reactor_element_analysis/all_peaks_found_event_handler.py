from qtpy.QtWidgets import QMenu
from qtpy import QtGui

from __code._utilities.table_handler import TableHandler


class AllPeaksFoundEventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def right_click(self):

        o_table = TableHandler(table_ui=self.parent.ui.elements_position_tableWidget)
        row, col = o_table.get_cell_selected()

        global_list_of_xy_max = self.parent.global_list_of_xy_max
        list_of_images = self.parent.list_of_images

        file_name_value = list_of_images[row]
        angle_value = global_list_of_xy_max[file_name_value]['x'][col]

        menu = QMenu(self.parent)

        file_name = menu.addAction("file name: {}".format(file_name_value))
        angle = menu.addAction("angle: {}".format(angle_value))

        action = menu.exec_(QtGui.QCursor.pos())
