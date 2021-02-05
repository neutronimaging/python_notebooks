from qtpy.QtWidgets import QFileDialog, QApplication
from qtpy import QtGui
import os
from NeuNorm.normalization import Normalization


class Export:

    def __init__(self, parent=None):
        self.parent = parent

    def run(self):
        working_dir = os.path.abspath(os.path.dirname(self.parent.working_dir))
        export_folder = QFileDialog.getExistingDirectory(self.parent,
                                                         caption="Select folder",
                                                         directory=working_dir)

        if export_folder:
            resize_and_overlay_images = self.parent.resize_and_overlay_images

            message = "Exporting overlaid images ... IN PROGRESS"
            self.parent.ui.statusbar.showMessage(message)
            self.parent.ui.statusbar.setStyleSheet("color: blue")

            self.parent.eventProgress.setMaximum(len(resize_and_overlay_images))
            self.parent.eventProgress.setValue(0)
            self.parent.eventProgress.setVisible(True)
            QtGui.QGuiApplication.processEvents()

            list_of_filename = self.parent.list_of_high_res_filename
            for _index, _overlay_image in enumerate(resize_and_overlay_images):

                _short_filemame = os.path.basename(list_of_filename[_index])
                o_norm = Normalization()
                o_norm.load(data=_overlay_image)
                o_norm.data['sample']['file_name'] = [_short_filemame]
                o_norm.export(folder=export_folder,
                              data_type='sample')
                self.parent.eventProgress.setValue(_index + 1)
                QtGui.QGuiApplication.processEvents()

            self.parent.eventProgress.setVisible(False)

            message = "Overlaid images exported in {}".format(export_folder)
            self.parent.ui.statusbar.showMessage(message, 10000)  # 10s
            self.parent.ui.statusbar.setStyleSheet("color: green")
