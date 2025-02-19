import os
import pyqtgraph.exporters
from qtpy import QtCore
from qtpy import QtGui
from qtpy.QtWidgets import QApplication
from IPython.core.display import HTML
from IPython.core.display import display


class ExportImages:

    ext = '.png'

    def __init__(self, parent=None, export_folder=''):
        self.parent = parent
        self.export_folder = export_folder

    def _create_output_file_name(self, file=''):
        if file == '':
            return ''

        basename_ext = os.path.basename(file)
        [basename, ext] = os.path.splitext(basename_ext)

        full_file_name = os.path.join(self.export_folder, basename + self.ext)
        return full_file_name

    def run(self):

        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.parent.eventProgress.setMinimum(1)
        self.parent.eventProgress.setMaximum(len(self.parent.data_dict['file_name']))
        self.parent.eventProgress.setValue(1)
        self.parent.eventProgress.setVisible(True)

        for _index, _file in enumerate(self.parent.data_dict['file_name']):
            output_file_name = self._create_output_file_name(file=_file)
            self.parent.ui.file_slider.setValue(_index)

            exporter = pyqtgraph.exporters.ImageExporter(self.parent.ui.image_view.view)

            exporter.params.param('width').setValue(2024, blockSignal=exporter.widthChanged)
            exporter.params.param('height').setValue(2014, blockSignal=exporter.heightChanged)

            exporter.export(output_file_name)

            self.parent.eventProgress.setValue(_index+2)
            QtGui.QGuiApplication.processEvents()

        QtGui.QGuiApplication.processEvents()

        display(HTML("Exported Images in Folder {}".format(self.export_folder)))
        self.parent.eventProgress.setVisible(False)
        QApplication.restoreOverrideCursor()
