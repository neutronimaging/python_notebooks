try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtGui import QMainWindow
except ImportError:
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtWidgets import QApplication, QMainWindow

from ipywidgets import widgets
from IPython.core.display import display, HTML
import ipywe.fileselector

import pyqtgraph as pg
import scipy.ndimage
import numpy as np
import os

from __code import file_handler
from __code.ui_rotate_and_crop import Ui_MainWindow as UiMainWindow


class RotateAndCropImages(QMainWindow):
    """Rotate and Crop Images"""

    grid_size = 100
    live_data = []

    height = 0
    width = 0
    nbr_files = 0

    # output
    rotated_working_data = []
    rotation_value = 0

    def __init__(self, parent=None, o_load=None):

        display(
            HTML(
                '<span style="font-size: 20px; color:blue">Select the rotation angle in the UI that poped up (maybe hidden behind this browser!)</span>'
            ))

        self.working_data = o_load.working_data
        self.rotated_working_data = o_load.working_data
        self.nbr_files = o_load.nbr_files

        self.list_images = o_load.list_images

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.init_statusbar()
        self.setWindowTitle("Select Rotation Angle for All Images")

        self.ui.image_view = pg.ImageView()
        self.ui.image_view.ui.roiBtn.hide()
        self.ui.image_view.ui.menuBtn.hide()

        bottom_layout = QtGui.QHBoxLayout()

        # file index slider
        label_1 = QtGui.QLabel("File Index")
        self.ui.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.ui.slider.setMaximum(len(self.list_images) - 1)
        self.ui.slider.setMinimum(0)
        self.ui.slider.valueChanged.connect(self.file_index_changed)

        # spacer
        spacer = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Minimum)

        # rotation value
        label_2 = QtGui.QLabel("Rotation (degrees)")
        self.ui.rotation_value = QtGui.QLineEdit('0')
        self.ui.rotation_value.setMaximumWidth(50)
        self.ui.rotation_value.returnPressed.connect(
            self.rotation_value_changed)

        if self.nbr_files > 1:
            bottom_layout.addWidget(label_1)
            bottom_layout.addWidget(self.ui.slider)

        bottom_layout.addItem(spacer)
        bottom_layout.addWidget(label_2)
        bottom_layout.addWidget(self.ui.rotation_value)

        bottom_widget = QtGui.QWidget()
        bottom_widget.setLayout(bottom_layout)

        vertical_layout = QtGui.QVBoxLayout()
        vertical_layout.addWidget(self.ui.image_view)
        vertical_layout.addWidget(bottom_widget)

        self.ui.widget.setLayout(vertical_layout)

        self.get_image_size()
        #        self.display_grid()
        self.display_crop_region()
        self.rotation_value_changed()

    def init_statusbar(self):
        self.eventProgress = QtGui.QProgressBar(self.ui.statusbar)
        self.eventProgress.setMinimumSize(20, 14)
        self.eventProgress.setMaximumSize(540, 100)
        self.eventProgress.setVisible(False)
        self.ui.statusbar.addPermanentWidget(self.eventProgress)

    def display_crop_region(self):
        [image_height, image_width] = [self.height, self.width]
        x0, y0 = 0, 0
        width = image_width - 1
        height = image_height - 1

        roi = pg.ROI(
            [x0, y0], [height, width], pen=(209, 230, 27), scaleSnap=True)
        roi.addScaleHandle([1, 1], [0, 0])
        self.ui.image_view.addItem(roi)
        self.roi = roi

    def get_selected_image(self, file_index):
        if type(self.working_data) is list:
            return self.working_data[_file_index]
        else:
            return self.working_data

    def display_image(self, image):
        image = self.get_selected_image(0)
        self.ui.image_view.setImage(image)

    def init_imageview(self):
        image = self.get_selected_image(0)
        self.ui.image_view.setImage(image)
        self.live_data = image

    def get_image_size(self):
        if len(np.shape(self.rotated_working_data)) > 2:
            [width, height] = np.shape(self.rotated_working_data[0])
        else:
            [width, height] = np.shape(self.rotated_working_data)

        self.width = width
        self.height = height

    def display_grid(self):
        [width, height] = [self.width, self.height]
        bin_size = self.grid_size
        x0 = 0
        y0 = 0

        pos_adj_dict = {}

        nbr_height_bins = np.float(height) / np.float(bin_size)
        real_height = y0 + np.int(nbr_height_bins) * np.int(bin_size)

        nbr_width_bins = np.float(width) / np.float(bin_size)
        read_width = x0 + np.int(nbr_width_bins) * np.int(bin_size)

        # pos (each matrix is one side of the lines)
        pos = []
        adj = []

        # vertical lines
        x = x0
        index = 0
        while (x <= x0 + width):
            one_edge = [x, y0]
            other_edge = [x, real_height]
            pos.append(one_edge)
            pos.append(other_edge)
            adj.append([index, index + 1])
            x += bin_size
            index += 2

        # horizontal lines
        y = y0
        while (y <= y0 + height):
            one_edge = [x0, y]
            other_edge = [read_width, y]
            pos.append(one_edge)
            pos.append(other_edge)
            adj.append([index, index + 1])
            y += bin_size
            index += 2

        pos = np.array(pos)
        adj = np.array(adj)

        line_color = (255, 0, 0, 155, 0.2)
        lines = np.array(
            [line_color for n in np.arange(len(pos))],
            dtype=[('red', np.ubyte), ('green', np.ubyte), ('blue', np.ubyte),
                   ('alpha', np.ubyte), ('width', float)])

        line_view_binning = pg.GraphItem()
        self.ui.image_view.addItem(line_view_binning)
        line_view_binning.setData(
            pos=pos, adj=adj, pen=lines, symbol=None, pxMode=False)

        self.line_view_binning = line_view_binning

    def rotation_value_changed(self):
        _rotation_value = np.float(str(self.ui.rotation_value.text()))

        if self.nbr_files > 1:
            _file_index = self.ui.slider.value()
            _data = self.working_data[_file_index]
        else:
            _data = self.working_data

        rotated_data = scipy.ndimage.interpolation.rotate(
            _data, _rotation_value)
        self.live_data = rotated_data
        #        self.ui.image_view.removeItem(self.line_view_binning)
        #       self.display_grid()
        self.ui.image_view.setImage(rotated_data)

    def rotate_and_crop_all(self):

        region = self.roi.getArraySlice(self.live_data,
                                        self.ui.image_view.imageItem)
        x0 = region[0][0].start
        x1 = region[0][0].stop - 1
        y0 = region[0][1].start
        y1 = region[0][1].stop - 1

        self.eventProgress.setValue(0)
        self.eventProgress.setMaximum(self.nbr_files)
        self.eventProgress.setVisible(True)

        _rotation_value = np.float(str(self.ui.rotation_value.text()))
        self.rotated_working_data = []
        for _index in np.arange(self.nbr_files):
            if self.nbr_files == 1:
                _data = self.working_data
            else:
                _data = self.working_data[_index]

            rotated_data = scipy.ndimage.interpolation.rotate(_data,
                                                              _rotation_value)
            rotated_data = rotated_data[x0:x1, y0:y1]
            self.rotated_working_data.append(rotated_data)
            self.eventProgress.setValue(_index + 1)
            QtGui.QApplication.processEvents()
            self.rotation_angle = _rotation_value

        # self.file_index_changed()
        #        self.ui.image_view.removeItem(self.line_view_binning)
        #        self.display_grid()

        self.eventProgress.setVisible(False)

    def apply_clicked(self):
        self.rotate_and_crop_all()
        self.close()

    def cancel_clicked(self):
        self.close()

    def file_index_changed(self):
        self.rotation_value_changed()

    def closeEvent(self, event=None):
        global rotation_angle
        rotation_angle = np.float(str(self.ui.rotation_value.text()))


class Export(object):

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

    def select_folder(self):

        display(HTML(
            '<span style="font-size: 20px; color:blue">Select where you want to create the rotated images folder!</span>'))

        self.output_folder_ui = ipywe.fileselector.FileSelectorPanel(instruction = 'Select Output Folder ...',
                                                                start_dir = self.working_dir,
                                                                type = 'directory')
        self.output_folder_ui.show()

    def get_folder(self):
        return os.path.abspath(self.output_folder_ui.selected)

    def export(self, new_folder='', data='', list_files=''):

        w = widgets.IntProgress()
        w.max = len(list_files)
        display(w)

        output_folder = self.get_folder()
        full_output_folder = os.path.join(output_folder, new_folder)
        if not os.path.exists(full_output_folder):
            os.makedirs(full_output_folder)

        for _index, _file in enumerate(list_files):
            _base_file_name = os.path.basename(_file)
            [_base, _] = os.path.splitext(_base_file_name)
            _full_file_name = os.path.join(full_output_folder, _base + '.tiff')
            file_handler.make_tiff(data=data[_index], filename=_full_file_name)

            w.value = _index + 1

        w.close()

        display(HTML(
            '<span style="font-size: 20px; color:blue">Files created in ' + full_output_folder + '</span>'))


