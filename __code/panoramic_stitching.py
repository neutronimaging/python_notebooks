from IPython.core.display import HTML
from IPython.display import display
import pyqtgraph as pg
import numpy as np
import os

try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtGui import QMainWindow
except ImportError:
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtWidgets import QApplication, QMainWindow

from NeuNorm.normalization import Normalization

from __code.ui_panoramic_stitching import Ui_MainWindow as UiMainWindow
from __code.file_folder_browser import FileFolderBrowser
from __code._panoramic_stitching.gui_initialization import GuiInitialization


class InterfaceHandler(FileFolderBrowser):

    def __init__(self, working_dir=''):
        super(InterfaceHandler, self).__init__(working_dir=working_dir)

    def load(self):
        list_images = self.list_images_ui.selected
        o_norm = Normalization()
        o_norm.load(file=list_images, notebook=True)
        self.o_norm = o_norm


class Interface(QMainWindow):

    master_dict = {}
    tableWidget_columns_size = [400, 400, 100]
    histogram_level = {'reference': [],
                       'target': []}
    pyqtgraph_image_view = {'reference': None,
                            'data': None}
    live_rois_id = {'reference': None,
                    'target': None}

    def __init__(self, parent=None, o_norm=None):

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
            (maybe hidden behind this browser!)</span>'))

        self.o_norm = o_norm

        self.list_files = self.o_norm.data['sample']['file_name']
        self.basename_list_files = [os.path.basename(_file) for _file in self.list_files]

        self.list_data = self.o_norm.data['sample']['data']

        self.list_reference = self.get_list_files(start_index=0, end_index=-1)
        self.list_target = self.get_list_files(start_index=1)

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Panoramic Stitching")

        o_initialization = GuiInitialization(parent=self)
        o_initialization.all()

    def get_list_files(self, start_index=0, end_index=None):
        if end_index is None:
            end_index = len(self.list_files)+1

        _list = {'files': self.list_files[start_index: end_index],
                 'data': self.list_data[start_index: end_index],
                 'basename_files': []}
        _list['basename_files'] = [os.path.basename(_file) for _file in _list['files']]
        return _list

    # event handler
    def reference_roi_changed(self):
        pass

    def target_roi_changed(self):
        pass

    def table_widget_selection_changed(self):
        reference_file_index_selected = self.get_reference_index_selected()

        # +1 because the target file starts at the second file
        target_file_index_selected = self.get_target_index_selected_from_row(row=reference_file_index_selected)

        reference_data = self.list_reference['data'][reference_file_index_selected]
        target_data = self.list_target['data'][target_file_index_selected]

        self.display_reference_data(data=reference_data)
        self.display_target_data(data=target_data)

    def display_reference_data(self, data=[]):
        self.display_data(data_type='reference', data=data)

    def display_target_data(self, data=[]):
        self.display_data(data_type='target', data=data)

    def display_data(self, data_type='reference', data=[]):

        ui = self.pyqtgraph_image_view[data_type]
        histogram_level = self.histogram_level[data_type]

        _view = ui.getView()
        _view_box = _view.getViewBox()
        # self._view_box = _view_box
        _state = _view_box.getState()

        first_update = False
        if histogram_level == []:
            first_update = True
        _histo_widget = ui.getHistogramWidget()
        self.histogram_level[data_type] = _histo_widget.getLevels()

        data = np.transpose(data)
        ui.setImage(data)

        _view_box.setState(_state)

        if not first_update:
            _histo_widget.setLevels(self.histogram_level[data_type][0],
                                    self.histogram_level[data_type][1])

    def roi_changed(self):
        print("roi changed")

    def get_reference_index_selected(self):
        _selection = self.ui.tableWidget.selectedRanges()[0]
        _row_selected = _selection.topRow()
        return _row_selected

    def get_target_index_selected_from_row(self, row=0):
        _widget = self.ui.tableWidget.cellWidget(row, 1)
        return _widget.currentIndex()

    def table_widget_target_image_changed(self, index):
        self.table_widget_selection_changed()

    def apply_clicked(self):
        # do stuff
        self.close()

    def cancel_clicked(self):
        self.close()

    def display_image(self, image):
        self.ui.image_view.setImage(image)

    def closeEvent(self, eventhere=None):
        print("Leaving Panoramic Stitching UI")



