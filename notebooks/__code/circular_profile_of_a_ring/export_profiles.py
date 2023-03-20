import numpy as np
from qtpy.QtWidgets import QFileDialog, QApplication
from qtpy import QtCore
from qtpy.QtGui import QGuiApplication
import os

from __code.circular_profile_of_a_ring.configuration_handler import ConfigurationHandler
from __code.file_handler import make_ascii_file


class ExportProfiles:

    def __init__(self, parent=None):
        self.parent = parent

    def run(self):
        default_file_name = os.path.abspath(os.path.basename(self.parent.working_dir)) + "_profiles.csv"
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
            QGuiApplication.processEvents()

            dict_profile = self.parent.dict_profile

            _config = ConfigurationHandler(parent=self.parent)
            dict_config = _config.get_config_dict()

            metadata = ["# working dir: {}".format(os.path.abspath(self.parent.working_dir))]
            metadata.append("# ring central pixel (x, y):({}, {})".format(dict_config['ring']['central_pixel']['x'],
                                                                        dict_config['ring']['central_pixel']['y']))
            metadata.append("# ring inner radius (pixel): {}".format(dict_config['ring']['radius']))
            metadata.append("# ring thickness (pixel): {}".format(dict_config['ring']['thickness']))

            metadata.append("# Label of columns:")
            nbr_row = len(dict_profile.keys())
            list_files = self.parent.list_short_files
            for _row in np.arange(nbr_row):
                _file = list_files[_row]
                metadata.append("# column {}: {}".format(_row+1, _file))

            metadata.append("#")
            metadata.append("Angle from top vertical (degrees), mean counts (see label of columns above)")

            data = []
            list_angles = self.parent.list_angles
            for _index_angle, _angle in enumerate(list_angles):
                _entry = [str(_angle)]
                for _row_index in dict_profile.keys():
                    _data_of_that_row = dict_profile[_row_index]['y_profile']
                    _entry.append(str(_data_of_that_row[_index_angle]))
                _str_entry = ", ".join(_entry)
                data.append(_str_entry)

            make_ascii_file(metadata=metadata,
                            data=data,
                            output_file_name=export_file_name,
                            dim='1d')

            self.parent.ui.statusbar.showMessage("{} ... Saved!".format(os.path.basename(export_file_name)), 10000)
            self.parent.ui.statusbar.setStyleSheet("color: green")

            QApplication.restoreOverrideCursor()
            QGuiApplication.processEvents()
