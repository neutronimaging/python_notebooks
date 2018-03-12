from IPython.core.display import HTML
from IPython.display import display
import os
import numpy as np
import pyqtgraph as pg
from pyqtgraph.dockarea import *

try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtGui import QMainWindow
except ImportError:
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtWidgets import QApplication, QMainWindow

from NeuNorm.normalization import Normalization

from __code.ui_gamma_filtering_tool  import Ui_MainWindow as UiMainWindow
from __code.file_folder_browser import FileFolderBrowser


class InterfaceHandler(FileFolderBrowser):

    def __init__(self, working_dir=''):
        super(InterfaceHandler, self).__init__(working_dir=working_dir)

    def get_list_of_files(self):
        return self.list_images_ui.selected


class Interface(QMainWindow):

    live_data = []

    table_columns_size = [700, 100, 100]

    raw_histogram_level = []
    filtered_histogram_level = []
    diff_filtered_histogram_level = []

    live_raw_image = []
    live_filtered_image = []

    def __init__(self, parent=None, list_of_files=None):

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
            (maybe hidden behind this browser!)</span>'))

        self.list_files = list_of_files

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        # self.init_statusbar()

        self.init_pyqtgraph()
        self.init_widgets()
        self.init_table()

        self.slider_moved(slider_position=1)

    def init_table(self):
        for _row, _file in enumerate(self.list_files):
            self.ui.tableWidget.insertRow(_row)

            _short_file = os.path.basename(_file)
            _item = QtGui.QTableWidgetItem(_short_file)
            self.ui.tableWidget.setItem(_row, 0, _item)

    def init_pyqtgraph(self):
        area = DockArea()
        area.setVisible(True)
        d1 = Dock("Raw", size=(200, 200))
        d2 = Dock("Gamma Filtered", size=(200, 200))
        d3 = Dock("Raw - Gamma", size=(200, 200))

        area.addDock(d1, 'left')
        area.addDock(d2, 'right', d1)
        area.addDock(d3, 'right')

        self.ui.raw_image_view = pg.ImageView(view=pg.PlotItem())
        self.ui.raw_image_view.ui.roiBtn.hide()
        self.ui.raw_image_view.ui.menuBtn.hide()
        d1.addWidget(self.ui.raw_image_view)

        self.ui.filtered_image_view = pg.ImageView(view=pg.PlotItem())
        self.ui.filtered_image_view.ui.roiBtn.hide()
        self.ui.filtered_image_view.ui.menuBtn.hide()
        d2.addWidget(self.ui.filtered_image_view)

        self.ui.diff_image_view = pg.ImageView(view=pg.PlotItem())
        self.ui.diff_image_view.ui.roiBtn.hide()
        self.ui.diff_image_view.ui.menuBtn.hide()
        d3.addWidget(self.ui.diff_image_view)

        vertical_layout = QtGui.QVBoxLayout()
        vertical_layout.addWidget(area)
        self.ui.image_widget.setLayout(vertical_layout)

    def init_widgets(self):
        table_column_size = self.table_columns_size
        for _col in np.arange(self.ui.tableWidget.columnCount()):
            self.ui.tableWidget.setColumnWidth(_col, table_column_size[_col])

        nbr_files = len(self.list_files)
        if nbr_files <= 1:
            self.ui.file_index_slider.setVisible(False)
            self.ui.file_index_value.setVisible(False)
            self.ui.file_index_label.setVisible(False)
        else:
            self.ui.file_index_slider.setMinimum(1)
            self.ui.file_index_slider.setMaximum(nbr_files)

    def slider_moved(self, slider_position):
        self.dispplay_raw_image(file_index=slider_position-1)
        self.display_corrected_image(file_index=slider_position-1)
        self.calculate_and_display_diff_image(file_index=slider_position-1)
        self.ui.file_index_value.setText(str(slider_position))

    def calculate_and_display_diff_image(self, file_index=1):
        _view = self.ui.diff_image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()

        first_update = False
        if self.diff_filtered_histogram_level == []:
            first_update = True
        _histo_widget = self.ui.diff_image_view.getHistogramWidget()
        self.diff_filtered_histogram_level = _histo_widget.getLevels()

        _image = self.live_raw_image - self.live_filtered_image

        self.ui.diff_image_view.clear()
        self.ui.diff_image_view.setImage(_image)
        _view_box.setState(_state)
        self.live_filtered_image = _image

        if not first_update:
            _histo_widget.setLevels(self.diff_filtered_histogram_level[0], self.diff_filtered_histogram_level[1])

    def display_corrected_image(self, file_index=0):
        _view = self.ui.filtered_image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()

        first_update = False
        if self.filtered_histogram_level == []:
            first_update = True
        _histo_widget = self.ui.filtered_image_view.getHistogramWidget()
        self.filtered_histogram_level = _histo_widget.getLevels()

        o_norm = Normalization()
        file_name = self.list_files[file_index]
        o_norm.load(file=file_name, gamma_filter=True)
        _image = o_norm.data['sample']['data'][0]

        self.ui.filtered_image_view.clear()
        self.ui.filtered_image_view.setImage(_image)
        _view_box.setState(_state)
        self.live_filtered_image = _image

        if not first_update:
            _histo_widget.setLevels(self.filtered_histogram_level[0], self.filtered_histogram_level[1])

    def display_raw_image(self, file_index):
        _view = self.ui.raw_image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()

        first_update = False
        if self.raw_histogram_level == []:
            first_update = True
        _histo_widget = self.ui.raw_image_view.getHistogramWidget()
        self.raw_histogram_level = _histo_widget.getLevels()

        o_norm = Normalization()
        file_name = self.list_files[file_index]
        o_norm.load(file=file_name, gamma_filter=False)
        _image = o_norm.data['sample']['data'][0]

        self.ui.raw_image_view.clear()
        self.ui.raw_image_view.setImage(_image)
        _view_box.setState(_state)
        self.live_raw_image = _image

        if not first_update:
            _histo_widget.setLevels(self.raw_histogram_level[0], self.raw_histogram_level[1])

    def init_statusbar(self):
        self.eventProgress = QtGui.QProgressBar(self.ui.statusbar)
        self.eventProgress.setMinimumSize(20, 14)
        self.eventProgress.setMaximumSize(540, 100)
        self.eventProgress.setVisible(False)
        self.ui.statusbar.addPermanentWidget(self.eventProgress)

    def apply_clicked(self):
        # do stuff
        self.close()

    def cancel_clicked(self):
        self.close()

    def file_index_changed(self):
        file_index = self.ui.slider.value()
        new_live_image = self.list_data[file_index]
        self.ui.image_view.setImage(new_live_image)
        self.ui.file_name.setText(self.list_files[file_index])

    def display_image(self, image):
        self.ui.image_view.setImage(image)

    def closeEvent(self, eventhere=None):
        print("Leaving Parameters Selection UI")



