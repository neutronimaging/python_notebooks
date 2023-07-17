from qtpy.QtWidgets import QMainWindow, QLabel, QHBoxLayout, QSlider, QSpacerItem
from qtpy.QtWidgets import QSizePolicy, QLineEdit, QWidget, QVBoxLayout, QProgressBar, QApplication
from qtpy import QtCore
import copy

from ipywidgets import widgets
from IPython.core.display import display, HTML

import pyqtgraph as pg
import scipy.ndimage
import numpy as np
import os

from NeuNorm.normalization import Normalization

from __code import load_ui
from __code import file_handler
from __code.ipywe import fileselector


class DataDictKeys:
    filename = "filename"
    data = "data"


class RotateAndCropImages(QMainWindow):
    """Rotate and Crop Images"""

    grid_size = 100
    live_data = []

    height = 0
    width = 0
    nbr_files = 0

    # output
    rotated_working_data = []
    rotation_angle = 0
    list_files = []

    # {0: {'filename': "/filename0", 'data': None},
    #  1: {'filename': "/filename1", 'data': None},
    #  ...
    # }
    data_dict = None

    def __init__(self, parent=None, o_load=None):

        display(
            HTML(
                '<span style="font-size: 20px; color:blue">Select the rotation angle in the UI that popped up (maybe '
                'hidden behind this browser!)</span>'
            ))

        self.data_dict = o_load.data_dict
        # self.rotated_data_dict = copy.deepcopy(self.data_dict)

        # self.working_data = o_load.working_data
        # self.rotated_working_data = o_load.working_data
        self.nbr_files = len(self.data_dict.keys())

        self.list_images = o_load.list_images

        QMainWindow.__init__(self, parent=parent)

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui', 'ui_rotate_and_crop.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.init_statusbar()
        self.setWindowTitle("Select Rotation Angle for All Images")

        self.ui.image_view = pg.ImageView()
        self.ui.image_view.ui.roiBtn.hide()
        self.ui.image_view.ui.menuBtn.hide()

        bottom_layout = QHBoxLayout()

        # spacer
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # rotation value
        label_2 = QLabel("Rotation (degrees)")
        self.ui.rotation_value = QLineEdit('0')
        self.ui.rotation_value.setMaximumWidth(50)
        self.ui.rotation_value.returnPressed.connect(
            self.rotation_value_changed)

        if self.nbr_files > 1:
            self.ui.file_index_groupBox.setVisible(True)
            self.ui.file_index_slider.setMaximum(self.nbr_files-1)
        else:
            self.ui.file_index_groupBox.setVisible(False)

        bottom_layout.addItem(spacer)
        bottom_layout.addWidget(label_2)
        bottom_layout.addWidget(self.ui.rotation_value)

        bottom_widget = QWidget()
        bottom_widget.setLayout(bottom_layout)

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.ui.image_view)
        vertical_layout.addWidget(bottom_widget)

        self.ui.widget.setLayout(vertical_layout)

        self.get_image_size()
        self.display_image()
        self.display_crop_region()
        self.rotation_value_changed()
        self.ui.number_of_files_label.setText(str(len(self.list_images)-1))

    def init_statusbar(self):
        self.eventProgress = QProgressBar(self.ui.statusbar)
        self.eventProgress.setMinimumSize(20, 14)
        self.eventProgress.setMaximumSize(540, 100)
        self.eventProgress.setVisible(False)
        self.ui.statusbar.addPermanentWidget(self.eventProgress)

    def image_slider_pressed(self):
        # self.rotation_value_changed()
        self.display_image()

    def image_slider_moved(self, index):
        # self.rotation_value_changed()
        self.display_image()

    def image_slider_released(self):
        # self.rotation_value_changed()
        self.display_image()

    def display_crop_region(self):
        [image_height, image_width] = [self.height, self.width]
        x0, y0 = 0, 0
        width = image_width - 1
        height = image_height - 1

        roi = pg.ROI(
            [x0, y0], [width, height], pen=(209, 230, 27), scaleSnap=True)
        roi.addScaleHandle([1, 1], [0, 0])
        self.ui.image_view.addItem(roi)
        self.roi = roi

    def get_selected_image(self, file_index=None):
        if file_index is None:
            file_index = self.ui.file_index_slider.value()

        if self.data_dict[file_index][DataDictKeys.data] is None:
            data = RotateAndCropImages.load_data(filename=self.data_dict[file_index][DataDictKeys.filename])
            self.data_dict[file_index][DataDictKeys.data] = data

        else:
            data = self.data_dict[file_index][DataDictKeys.data]
        return data

    def display_image(self):
        index_image = self.ui.file_index_slider.value()
        self.ui.image_index_label.setText(str(index_image))
        image = self.get_selected_image(index_image)
        self.ui.image_view.setImage(np.transpose(image))

    def init_imageview(self):
        image = self.get_selected_image(0)
        self.ui.image_view.setImage(image)
        self.live_data = image

    def get_image_size(self):
        data = self.get_selected_image(0)
        [height, width] = np.shape(data)

        self.width = width
        self.height = height

    def display_grid(self):
        [width, height] = [self.width, self.height]
        bin_size = self.grid_size
        x0 = 0
        y0 = 0

        pos_adj_dict = {}

        nbr_height_bins = float(height) / float(bin_size)
        real_height = y0 + int(nbr_height_bins) * int(bin_size)

        nbr_width_bins = float(width) / float(bin_size)
        read_width = x0 + int(nbr_width_bins) * int(bin_size)

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

    @staticmethod
    def load_data(filename):
        o_norm = Normalization()
        o_norm.load(file=filename, notebook=False)
        data = np.squeeze(o_norm.data['sample']['data'][0])
        return data

    def get_or_load_data(self, file_index=0):
        """
        check if the data has already been loaded in self.data_dict. If it didn't, load it and return the
        array. If it's already there, just return the array
        """
        if self.data_dict[file_index][DataDictKeys.data] is None:
            data = RotateAndCropImages.load_data(self.data_dict[file_index][DataDictKeys.filename])
            self.data_dict[file_index][DataDictKeys.data] = data
            return data
        else:
            return self.data_dict[file_index][DataDictKeys.data]

    def rotation_value_changed(self):
        _rotation_value = float(str(self.ui.rotation_value.text()))

        _file_index = self.ui.file_index_slider.value()
        _data = self.get_or_load_data(file_index=_file_index)

        rotated_data = scipy.ndimage.interpolation.rotate(
            _data, _rotation_value)

        # [x0, x1, y0, y1] = self.get_crop_region()
        # rotated_data = rotated_data[x0:x1, y0:y1]

        rotated_data = np.transpose(rotated_data)
        self.ui.image_view.setImage(rotated_data)

    def get_crop_region(self):
        data = self.get_selected_image()
        # data = self.live_data
        region = self.roi.getArraySlice(np.transpose(data),
                                        self.ui.image_view.imageItem)
        x1 = region[0][0].stop - 1
        y1 = region[0][1].stop - 1
        x0 = region[0][1].start
        y0 = region[0][0].start

        return [x0, x1, y0, y1]

    def rotate_and_crop_all(self):
        [x0, x1, y0, y1] = self.get_crop_region()

        self.eventProgress.setValue(0)
        self.eventProgress.setMaximum(self.nbr_files)
        self.eventProgress.setVisible(True)

        _rotation_value = float(str(self.ui.rotation_value.text()))
        self.rotated_data_dict = {}
        for file_index in self.data_dict.keys():
            data = self.get_selected_image(file_index=file_index)
            if float(_rotation_value) != float(0.0):
                rotated_data = scipy.ndimage.interpolation.rotate(data,
                                                                  _rotation_value)
                rotated_data = rotated_data[y0:y1, x0:x1]
            else:
                rotated_data = data[y0:y1, x0:x1]

            self.rotated_data_dict[file_index] = {DataDictKeys.filename: self.data_dict[file_index][DataDictKeys.filename],
                                                  DataDictKeys.data: rotated_data}

            self.eventProgress.setValue(file_index + 1)
            QApplication.processEvents()
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
        # global rotation_angle
        rotation_angle = float(str(self.ui.rotation_value.text()))


class Export(object):

    def __init__(self, working_dir='', data_dict=None, rotation_angle=0):
        self.working_dir = working_dir
        self.data_dict = data_dict
        self.rotation_angle = rotation_angle

    def select_folder(self):

        display(HTML(
           '<span style="font-size: 20px; color:blue">Select where you want to create the rotated images folder!</span>'))

        self.output_folder_ui = fileselector.FileSelectorPanel(instruction='Select Output Folder ...',
                                                               start_dir=self.working_dir,
                                                               type='directory',
                                                               next=self.export)

        self.output_folder_ui.show()

    def export(self, output_folder):

        new_folder = 'rotated_{}deg'.format(self.rotation_angle)

        data_dict = self.data_dict

        w = widgets.IntProgress()
        w.max = len(data_dict.keys())
        display(w)

        output_folder = os.path.abspath(output_folder)
        full_output_folder = os.path.join(output_folder, new_folder)
        if not os.path.exists(full_output_folder):
            os.makedirs(full_output_folder)

        for _index in data_dict.keys():
            _file = data_dict[_index][DataDictKeys.filename]
            data = data_dict[_index][DataDictKeys.data]
            _base_file_name = os.path.basename(_file)
            [_base, _] = os.path.splitext(_base_file_name)
            _full_file_name = os.path.join(full_output_folder, _base + '.tiff')
            file_handler.make_tiff(data=data, filename=_full_file_name)
            w.value = _index + 1

        w.close()

        display(HTML(''))
        display(HTML(
           '<span style="font-size: 20px; color:blue">Files created in ' + full_output_folder + '</span>'))
