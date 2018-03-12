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

    table_columns_size = [800, 150, 150]

    raw_histogram_level = []
    filtered_histogram_level = []
    diff_filtered_histogram_level = []

    live_raw_image = []
    live_filtered_image = []
    live_diff_image = []

    raw_image_size = []

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
        self.init_statusbar()
        self.slider_moved(slider_position=1)

    def init_statusbar(self):
        _width_labels = 40
        _height_labels = 30

        # x0, y0, width and height of selection
        _x_label = QtGui.QLabel("X:")
        self.x_value = QtGui.QLabel("N/A")
        self.x_value.setFixedSize(_width_labels, _height_labels)
        _y_label = QtGui.QLabel("Y:")
        self.y_value = QtGui.QLabel("N/A")
        self.y_value.setFixedSize(_width_labels, _height_labels)
        raw_label = QtGui.QLabel("  Counts Raw:")
        self.raw_value = QtGui.QLabel("N/A")
        self.raw_value.setFixedSize(_width_labels, _height_labels)
        filtered_label = QtGui.QLabel("  Counts Filtered:")
        self.filtered_value = QtGui.QLabel("N/A")
        self.filtered_value.setFixedSize(_width_labels, _height_labels)
        diff_label = QtGui.QLabel("  Counts Diff.:")
        self.diff_value = QtGui.QLabel("N/A")
        self.diff_value.setFixedSize(_width_labels, _height_labels)

        hori_layout = QtGui.QHBoxLayout()
        hori_layout.addWidget(_x_label)
        hori_layout.addWidget(self.x_value)
        hori_layout.addWidget(_y_label)
        hori_layout.addWidget(self.y_value)
        hori_layout.addWidget(raw_label)
        hori_layout.addWidget(self.raw_value)
        hori_layout.addWidget(filtered_label)
        hori_layout.addWidget(self.filtered_value)
        hori_layout.addWidget(diff_label)
        hori_layout.addWidget(self.diff_value)

        # spacer
        spacerItem = QtGui.QSpacerItem(22520, 40, QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Expanding)
        hori_layout.addItem(spacerItem)

        # add status bar in main ui
        bottom_widget = QtGui.QWidget()
        bottom_widget.setLayout(hori_layout)
        self.ui.statusbar.addPermanentWidget(bottom_widget)

    def init_table(self):
        for _row, _file in enumerate(self.list_files):
            self.ui.tableWidget.insertRow(_row)

            _short_file = os.path.basename(_file)
            _item = QtGui.QTableWidgetItem(_short_file)
            self.ui.tableWidget.setItem(_row, 0, _item)

    def mouse_moved_in_any_image(self, evt, image='raw'):
        pos = evt[0]

        if image == 'raw':
            image_view = self.ui.raw_image_view
        elif image == 'filtered':
            image_view = self.ui.filtered_image_view
        else:
            image_view = self.ui.diff_image_view

        if image_view.view.sceneBoundingRect().contains(pos):

            [height, width] = self.raw_image_size

            #mouse_point = self.ui.raw_image_view.view.vb.mapSceneToView(pos)
            mouse_point = image_view.view.getViewBox().mapSceneToView(pos)
            mouse_x = int(mouse_point.x())
            mouse_y = int(mouse_point.y())

            if (mouse_x >= 0 and mouse_x < width) and \
                    (mouse_y >= 0 and mouse_y < height):
                self.x_value.setText(str(mouse_x))
                self.y_value.setText(str(mouse_y))

                _raw_value = self.live_raw_image[mouse_y, mouse_x]
                _filtered_value = self.live_filtered_image[mouse_y, mouse_x]
                _diff_value = _raw_value - _filtered_value

                self.raw_value.setText("{:.03f}".format(_raw_value))
                self.filtered_value.setText("{:.03f}".format(_filtered_value))
                self.diff_value.setText("{:.03f}".format(_diff_value))

                ### does not work !!!!!!
                self.raw_hline.setPos(mouse_point.y())
                self.raw_vline.setPos(mouse_point.x())

                self.filtered_hline.setPos(mouse_point.y())
                self.filtered_vline.setPos(mouse_point.x())

                self.diff_hline.setPos(mouse_point.y())
                self.diff_vline.setPos(mouse_point.x())

            else:
                self.x_value.setText("N/A")
                self.y_value.setText("N/A")
                self.raw_value.setText("N/A")
                self.filtered_value.setText("N/A")
                self.diff_value.setText("N/A")

    def mouse_moved_in_raw_image(self, evt):
        self.mouse_moved_in_any_image(evt, image='raw')

    def mouse_moved_in_filtered_image(self, evt):
        self.mouse_moved_in_any_image(evt, image='filtered')

    def mouse_moved_in_diff_image(self, evt):
        self.mouse_moved_in_any_image(evt, image='diff')

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
        self.ui.raw_image_view.view.setAutoVisible(y=True)
        # self.raw_vLine = pg.InfiniteLine(angle=90, movable=False)
        # self.raw_hLine = pg.InfiniteLine(angle=0, movable=False)
        # self.ui.raw_image_view.addItem(self.raw_vLine, ignoreBounds=True)
        # self.ui.raw_image_view.addItem(self.raw_hLine, ignoreBounds=True)
        self.raw_proxy = pg.SignalProxy(self.ui.raw_image_view.view.scene().sigMouseMoved,
                                    rateLimit=60,
                                    slot=self.mouse_moved_in_raw_image)
        d1.addWidget(self.ui.raw_image_view)

        self.ui.filtered_image_view = pg.ImageView(view=pg.PlotItem())
        self.ui.filtered_image_view.ui.roiBtn.hide()
        self.ui.filtered_image_view.ui.menuBtn.hide()
        # self.filtered_vLine = pg.InfiniteLine(angle=90, movable=False)
        # self.filtered_hLine = pg.InfiniteLine(angle=0, movable=False)
        # self.ui.filtered_image_view.addItem(self.filtered_vLine, ignoreBounds=True)
        # self.ui.filtered_image_view.addItem(self.filtered_hLine, ignoreBounds=True)
        self.filtered_proxy = pg.SignalProxy(self.ui.filtered_image_view.view.scene().sigMouseMoved,
                                    rateLimit=60,
                                    slot=self.mouse_moved_in_filtered_image)
        d2.addWidget(self.ui.filtered_image_view)

        self.ui.diff_image_view = pg.ImageView(view=pg.PlotItem())
        self.ui.diff_image_view.ui.roiBtn.hide()
        self.ui.diff_image_view.ui.menuBtn.hide()
        # self.diff_vLine = pg.InfiniteLine(angle=90, movable=False)
        # self.diff_hLine = pg.InfiniteLine(angle=0, movable=False)
        # self.ui.diff_image_view.addItem(self.diff_vLine, ignoreBounds=True)
        # self.ui.diff_image_view.addItem(self.diff_hLine, ignoreBounds=True)
        self.diff_proxy = pg.SignalProxy(self.ui.diff_image_view.view.scene().sigMouseMoved,
                                    rateLimit=60,
                                    slot=self.mouse_moved_in_diff_image)
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
        self.display_raw_image(file_index=slider_position-1)
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
        self.live_diff_image = _image

        if not first_update:
            _histo_widget.setLevels(self.diff_filtered_histogram_level[0],
                                    self.diff_filtered_histogram_level[1])

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
        _image = np.transpose(_image)
        self.ui.filtered_image_view.setImage(_image)
        _view_box.setState(_state)
        self.live_filtered_image = _image

        if not first_update:
            _histo_widget.setLevels(self.filtered_histogram_level[0],
                                    self.filtered_histogram_level[1])

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

        # self.ui.raw_image_view.clear()
        _image = np.transpose(_image)
        self.ui.raw_image_view.setImage(_image)
        _view_box.setState(_state)
        self.live_raw_image = _image

        self.raw_image_size = np.shape(_image)

        if not first_update:
            _histo_widget.setLevels(self.raw_histogram_level[0],
                                    self.raw_histogram_level[1])

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



