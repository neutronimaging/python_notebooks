from qtpy import QtGui

from __code.metadata_overlapping_images.metadata_string_format_handler import MetadataStringFormatLauncher


class MetadataTableHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def right_click(self, position=None):
        menu = QtGui.QMenu(self.parent)

        _format = menu.addAction("Clean String ...")

        action = menu.exec_(QtGui.QCursor.pos())

        if action == _format:
            self.format_metadata_column()

    def format_metadata_column(self):
        MetadataStringFormatLauncher(parent=self.parent)
