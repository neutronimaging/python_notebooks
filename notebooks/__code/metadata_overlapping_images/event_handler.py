from qtpy import QtGui
from qtpy.QtWidgets import QMenu

from __code.metadata_overlapping_images.metadata_string_format_handler import MetadataStringFormatLauncher
from .get import Get


class MetadataTableHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def right_click(self, position=None):
        o_get = Get(parent=self.parent)
        column_selected = o_get.metadata_column_selected()

        if column_selected == 1:
            return

        menu = QMenu(self.parent)

        _x_axis = None
        _y_axis = None
        if column_selected in [0, 2, 3]:
            if column_selected == self.parent.x_axis_column_index:
                x_axis_string = self.parent.xy_axis_menu_logo['enable'] + "X-axis"
            else:
                x_axis_string = self.parent.xy_axis_menu_logo['disable'] + "X-axis"
            _x_axis = menu.addAction(x_axis_string)

            if column_selected == self.parent.y_axis_column_index:
                y_axis_string = self.parent.xy_axis_menu_logo['enable'] + "Y-axis"
            else:
                y_axis_string = self.parent.xy_axis_menu_logo['disable'] + "Y-axis"
            _y_axis = menu.addAction(y_axis_string)

        _format = None
        if column_selected in [2, 3]:
            menu.addSeparator()
            _format = menu.addAction("Clean String ...")

        action = menu.exec_(QtGui.QCursor.pos())

        if action == _format:
            self.format_metadata_column()

        elif action == _x_axis:
            self.parent.x_axis_column_index = column_selected
            self.parent.update_metadata_pyqt_ui()

        elif action == _y_axis:
            self.parent.y_axis_column_index = column_selected
            self.parent.update_metadata_pyqt_ui()

    def format_metadata_column(self):
        MetadataStringFormatLauncher(parent=self.parent)
