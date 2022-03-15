from qtpy.QtWidgets import QFileDialog, QApplication
from pathlib import Path
import numpy as np
import os

from __code._utilities.file import make_or_reset_folder
from __code.outliers_filtering.event_handler import EventHandler
from __code.outliers_filtering.algorithm import Algorithm


class Export:

    def __init__(self, parent=None):
        self.parent = parent

    def export(self):
        base_folder = Path(self.parent.working_dir)
        directory = str(base_folder.parent)
        _export_folder = QFileDialog.getExistingDirectory(self.parent,
                                                          directory=directory,
                                                          caption="Select Output Folder")

        if _export_folder:

            export_folder_name = os.path.join(_export_folder, str(base_folder.name) + "_outliers_corrected")
            make_or_reset_folder(export_folder_name)

            list_file = self.parent.list_files
            o_event = EventHandler(parent=self.parent)

            self.parent.eventProgress.setMaximum(len(list_file))
            self.parent.eventProgress.setValue(0)
            self.parent.eventProgress.setVisible(True)
            for _row, _file in enumerate(list_file):

                o_norm = o_event.load_data_object(file_name=_file)
                o_algo = Algorithm(parent=self.parent,
                                   data=np.squeeze(o_norm.data['sample']['data']))
                o_algo.run()
                data_corrected = o_algo.get_processed_data()
                o_norm.data['sample']['data'][0] = data_corrected
                o_norm.export(folder=export_folder_name,
                              data_type='sample')
                del o_norm
                del o_algo

                self.parent.eventProgress.setValue(_row)
                QApplication.processEvents()

            self.parent.eventProgress.setVisible(False)
            QApplication.processEvents(True)
