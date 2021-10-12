from qtpy import QtGui

from __code.metadata_overlapping_images.metadata_string_format_handler import MetadataStringFormatLauncher
from .get import Get


class MetadataTableHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def right_click(self, position=None):
        o_get = Get(parent=self.parent)
        column_selected = o_get.metadata_column_selected()

        if column_selected == 2:
            return

        print(f"column_selected: {column_selected}")

        menu = QtGui.QMenu(self.parent)

        _format = menu.addAction("Clean String ...")

        action = menu.exec_(QtGui.QCursor.pos())

        if action == _format:
            self.format_metadata_column()

    def format_metadata_column(self):
        MetadataStringFormatLauncher(parent=self.parent)
