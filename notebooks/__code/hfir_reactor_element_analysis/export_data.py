import numpy as np
from qtpy.QtWidgets import QFileDialog, QApplication
from qtpy import QtCore, QtGui
import os

from __code.file_handler import make_ascii_file


class ExportData:

    def __init__(self, parent=None):
        self.parent = parent

    def run(self):
        default_file_name = os.path.abspath(os.path.basename(self.parent.working_dir)) + "_elements_position.csv"
        working_dir = os.path.dirname(self.parent.working_dir)
        directory = os.path.join(working_dir, default_file_name)
        export_file_name = QFileDialog.getSaveFileName(self.parent,
                                                       caption="Select or define filename ...",
                                                       directory=directory,
                                                       filter="ascii(*.csv)",
                                                       initialFilter='ascii')

        if export_file_name[0]:

            export_file_name = export_file_name[0]
            self.parent.ui.statusbar.showMessage("Saving {} ... IN PROGRESS".format(os.path.basename(export_file_name)))
            self.parent.ui.statusbar.setStyleSheet("color: blue")
            QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            QtGui.QGuiApplication.processEvents()

            global_list_of_xy_max = self.parent.global_list_of_xy_max

            metadata = []
            data = []
            list_of_images = self.parent.o_selection.column_labels[1:]
            for _index_file, _file in enumerate(list_of_images):
                metadata.append("#{}: {}".format(_index_file, _file))
                _entry = global_list_of_xy_max[_file]['x']
                _row_entry = [str(_index_file)]
                for _value in _entry:
                    _row_entry.append(str(_value))
                _str_entry = ", ".join(_row_entry)
                data.append(_str_entry)

            metadata.append("#")
            make_ascii_file(data=data,
                            metadata=metadata,
                            output_file_name=export_file_name,
                            dim='1d')

            self.parent.ui.statusbar.showMessage("{} ... Saved!".format(os.path.basename(export_file_name)), 10000)
            self.parent.ui.statusbar.setStyleSheet("color: green")
            QApplication.restoreOverrideCursor()
            QtGui.QGuiApplication.processEvents()
