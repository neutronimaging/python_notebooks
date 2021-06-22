import os
import logging
from qtpy.QtWidgets import QFileDialog
from qtpy.QtGui import QGuiApplication

from NeuNorm.normalization import Normalization

from __code.file_handler import get_file_extension
from __code.mcp_chips_corrector.event_handler import EventHandler
from __code._utilities.file import make_or_reset_folder


class Export:

    def __init__(self, parent=None):
        self.parent = parent

    def correct_all_images(self):
        export_folder = QFileDialog.getExistingDirectory(self.parent,
                                                         directory=self.parent.working_dir,
                                                         caption="Select output folder",
                                                         options=QFileDialog.ShowDirsOnly)

        QGuiApplication.processEvents()  # to close QFileDialog

        if export_folder:

            base_input_folder = os.path.basename(os.path.abspath(self.parent.o_corrector.input_working_folder))
            export_folder = os.path.join(export_folder, base_input_folder + "_corrected")
            make_or_reset_folder(export_folder)

            logging.info("exporting all corrected images:")
            logging.info(f"-> export folder: {export_folder}")
            working_data = self.parent.working_data
            nbr_files = len(working_data)
            self.parent.ui.statusbar.showMessage("Correcting all images ...")

            self.parent.eventProgress.setMaximum(nbr_files)
            self.parent.eventProgress.setVisible(True)
            working_list_files = self.parent.working_list_files

            for _index_file, _data in enumerate(working_data):
                o_event = EventHandler(parent=self.parent)
                corrected_data = o_event.calculate_contrast_image(raw_image=_data)
                o_norm = Normalization()
                o_norm.load(data=corrected_data, notebook=False)

                short_file_name = os.path.basename(working_list_files[_index_file])
                file_extension = get_file_extension(short_file_name)
                o_norm.data['sample']['file_name'] = [short_file_name]
                o_norm.export(folder=export_folder,
                              data_type='sample',
                              file_type=file_extension)

                self.parent.eventProgress.setValue(_index_file + 1)
                QGuiApplication.processEvents()
                logging.info(f"-> exported file: {self.parent.o_corrector.working_list_files[_index_file]}")

            self.parent.ui.statusbar.showMessage("Corrected images are in folder {}".format(export_folder), 10000)
            self.parent.eventProgress.setVisible(False)
