from qtpy.QtWidgets import QFileDialog, QApplication
from qtpy import QtGui
import os

from NeuNorm.normalization import Normalization

from __code.file_handler import make_or_reset_folder


class Export:

    def __init__(self, parent=None):
        self.parent = parent

    def run(self):
        working_dir = os.path.abspath(os.path.dirname(self.parent.working_dir))
        export_folder = QFileDialog.getExistingDirectory(self.parent,
                                                         caption="Select folder",
                                                         directory=working_dir)

        if export_folder:

            # make own folder where the data will be exported
            short_high_res_input_folder = os.path.basename(self.parent.high_res_input_folder)
            short_low_res_input_folder = os.path.basename(self.parent.low_res_input_folder)
            output_folder = "{}_and_{}_overlaid".format(short_low_res_input_folder,
                                                        short_high_res_input_folder)
            full_output_folder = os.path.join(export_folder, output_folder)
            make_or_reset_folder(full_output_folder)

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
                o_norm.export(folder=full_output_folder,
                              data_type='sample')
                self.parent.eventProgress.setValue(_index + 1)
                QtGui.QGuiApplication.processEvents()

            self.parent.eventProgress.setVisible(False)

            message = "Overlaid images exported in {}".format(full_output_folder)
            self.parent.ui.statusbar.showMessage(message, 20000)  # 20s
            self.parent.ui.statusbar.setStyleSheet("color: green")
