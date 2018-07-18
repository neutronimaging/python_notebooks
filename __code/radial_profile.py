#from ipywidgets.widgets import interact
from ipywidgets import widgets
from IPython.core.display import HTML
from IPython.display import display
import ipywe.fileselector

import matplotlib.pyplot as plt

import numpy as np
import os

import pyqtgraph as pg

try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtGui import QMainWindow
except ImportError:
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtWidgets import QApplication, QMainWindow

from __code import file_handler
from __code.ui_radial_profile import Ui_MainWindow as UiMainWindow
from __code.file_folder_browser import FileFolderBrowser

from sectorizedradialprofile.calculate_radial_profile import CalculateRadialProfile


class RadialProfile(FileFolderBrowser):

    nbr_files = 0
    images_dimension = {'height': 0,
                        'width': 0}

    working_data = []
    working_dir = ''
    list_images = []
    profile_data = []

    def __init__(self, working_dir=''):
        super(RadialProfile, self).__init__(working_dir=working_dir)

    def load_images(self):
        list_images = self.list_images_ui.selected

        if list_images:

            w = widgets.IntProgress()
            w.max = len(list_images)
            display(w)

            working_data = []
            for _index, _file in enumerate(list_images):
                _data = np.array(file_handler.load_data(_file))
                _data[_data == np.inf] = np.NaN  # removing inf values
                _data[np.isnan(_data)] = 0
                working_data.append(_data)
                w.value = _index + 1

            [self.nbr_files, self.images_dimension['height'], self.images_dimension['width']] = np.shape(working_data)
            self.working_data = np.squeeze(working_data)
            self.working_dir = os.path.dirname(list_images[0])
            self.list_images = list_images

    def calculate(self, center={}, angle_range={}):

        self.center = center
        self.angle_range = angle_range

        w = widgets.IntProgress()
        w.max = self.nbr_files
        display(w)

        _array_profile = []

        for _index in np.arange(self.nbr_files):
            o_calculation =  CalculateRadialProfile(data=self.working_data[_index], center=center, angle_range=angle_range)
            o_calculation.calculate()

            _profile = o_calculation.radial_profile
            _array_profile.append(_profile)

            w.value = _index + 1

        self.profile_data = _array_profile

    def plot(self):
        plt.figure()
        for _index, _profile in enumerate(self.profile_data):
            plt.plot(_profile, label='profile #{}'.format(_index))
            plt.legend(loc=2)

    def select_export_folder(self):
        self.export_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select Output Folder ...',
                                                         type = 'directory',
                                                         start_dir=self.working_dir)
        self.export_ui.show()

    def export(self):
        output_folder = self.export_ui.selected
        if output_folder:

            for _index, _file in enumerate(self.list_images):

                [input_image_base_name, ext] = os.path.splitext(os.path.basename(_file))
                output_file_name = os.path.join(output_folder,
                                                input_image_base_name + '_profile_c_x{}_y{}_angle_{}_to_{}.txt'.format(
                                                    self.center['x0'], self.center['y0'],
                                                    self.angle_range['from'], self.angle_range['to']))
                output_file_name = os.path.abspath(output_file_name)

                text = []
                text.append("# source image: {}".format(_file))
                text.append("# center [x0, y0]: [{},{}]".format(self.center['x0'], self.center['y0']))
                text.append(
                    "# angular range from {}degrees to {}degrees".format(self.angle_range['from'], self.angle_range['to']))
                text.append('')
                text.append('#pixel_from_center, Average_counts')
                data = list(zip(np.arange(len(self.profile_data[_index])), self.profile_data[_index]))

                file_handler.make_ascii_file(metadata=text, data=data, output_file_name=output_file_name)

                display(HTML('<span style="font-size: 20px; color:blue">File created: ' + output_file_name + '</span>'))


class SelectRadialParameters(QMainWindow):

    grid_size = 200
    live_data = []

    sector_g = None

    from_angle_line = None
    to_angle_line = None

    guide_color_slider = {'red': 255,
                          'green': 0,
                          'blue': 255,
                          'alpha': 255}

    sector_range = {'from': 0,
                    'to': 90}

    corners = {'top_right': np.NaN,
               'bottom_right': np.NaN,
               'bottom_left': np.NaN,
               'top_left': np.NaN}

    hLine = None
    vLine = None

    height = np.NaN
    width = np.NaN

    angle_0 = None
    angle_90 = None
    angle_180 = None
    angle_270 = None

    histogram_level = []

    # def __init__(self, parent=None, o_profile=None):
    def __init__(self, parent=None, working_dir='', data_dict=None):

        display(HTML('<span style="font-size: 20px; color:blue">Select the center of the circle and the angular sector in the UI that poped up \
            (maybe hidden behind this browser!)</span>'))

        # o_profile.load_images()
        self.list_images = data_dict['file_name']
        self.working_data = data_dict['data']
        self.rotated_working_data = data_dict['data']
        [self.height, self.width] = np.shape(self.working_data[0])

        # self.rotated_working_data = o_profile.working_data
        # self.working_data = o_profile.working_data
        # self.list_images = o_profile.list_images
        # self.height = o_profile.images_dimension['height']
        # self.width = o_profile.images_dimension['width']

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.init_statusbar()
        self.setWindowTitle("Define center and sector of profile")

        self.ui.image_view = pg.ImageView(view=pg.PlotItem())
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
        spacer = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)

        bottom_layout.addWidget(label_1)
        bottom_layout.addWidget(self.ui.slider)
        bottom_layout.addItem(spacer)

        bottom_widget = QtGui.QWidget()
        bottom_widget.setLayout(bottom_layout)

        vertical_layout = QtGui.QVBoxLayout()
        vertical_layout.addWidget(self.ui.image_view)
        vertical_layout.addWidget(bottom_widget)

        self.ui.widget.setLayout(vertical_layout)

        self.init_widgets()
        self.display_grid()
        self.file_index_changed()
        self.init_crosshair()

    def init_crosshair(self):
        x0 = float(str(self.ui.circle_x.text()))
        y0 = float(str(self.ui.circle_y.text()))

        self.vLine = pg.InfiniteLine(pos=x0, angle=90, movable=True)
        self.hLine = pg.InfiniteLine(pos=y0, angle=0, movable=True)

        self.vLine.sigDragged.connect(self.manual_circle_center_changed)
        self.hLine.sigDragged.connect(self.manual_circle_center_changed)

        self.ui.image_view.addItem(self.vLine, ignoreBounds=False)
        self.ui.image_view.addItem(self.hLine, ignoreBounds=False)

    def init_widgets(self):
        self.ui.circle_y.setText(str(np.int(self.width / 2)))
        self.ui.circle_x.setText(str(np.int(self.height / 2)))
        # self.ui.lineEdit.setText(str(self.grid_size))

        self.ui.guide_red_slider.setValue(self.guide_color_slider['red'])
        self.ui.guide_green_slider.setValue(self.guide_color_slider['green'])
        self.ui.guide_blue_slider.setValue(self.guide_color_slider['blue'])
        self.ui.guide_alpha_slider.setValue(self.guide_color_slider['alpha'])

        self.ui.sector_from_value.setText(str(self.sector_range['from']))
        self.ui.sector_to_value.setText(str(self.sector_range['to']))

        self.sector_radio_button_changed()

    def grid_slider_moved(self, value):
        self.grid_size_changed()

    def grid_slider_pressed(self):
        self.grid_size_changed()

    def update_angle_label_position(self):

        x0 = np.int(str(self.ui.circle_x.text()))
        y0 = np.int(str(self.ui.circle_y.text()))

        # add angle 0, 90, 180 and 270 labels
        if self.angle_0 is None:
            self.angle_0 = pg.TextItem(text=u'0\u00b0', anchor=(0, 1))
            self.angle_90 = pg.TextItem(text=u'90\u00b0', anchor=(0, 1))
            self.angle_180 = pg.TextItem(text=u'180\u00b0', anchor=(0, 0))
            self.angle_270 = pg.TextItem(text=u'270\u00b0', anchor=(1, 1))

            self.ui.image_view.addItem(self.angle_0)
            self.ui.image_view.addItem(self.angle_90)
            self.ui.image_view.addItem(self.angle_180)
            self.ui.image_view.addItem(self.angle_270)

        self.angle_0.setPos(np.int(x0), 0)
        self.angle_90.setPos(self.height, y0)
        self.angle_180.setPos(x0, self.width)
        self.angle_270.setPos(0, y0)

    def remove_angle_label(self):

        if self.angle_0:
            self.ui.image_view.removeItem(self.angle_0)
            self.ui.image_view.removeItem(self.angle_90)
            self.ui.image_view.removeItem(self.angle_180)
            self.ui.image_view.removeItem(self.angle_270)

            self.angle_0 = None
            self.angle_90 = None
            self.angle_180 = None
            self.angle_270 = None

    def sector_radio_button_changed(self):

        is_full_circle = self.ui.sector_full_circle.isChecked()
        if is_full_circle:
            _status_sector = False
            self.remove_angle_label()
        else:
            _status_sector = True
            self.update_angle_label_position()

        self.ui.sector_from_label.setEnabled(_status_sector)
        self.ui.sector_from_value.setEnabled(_status_sector)
        self.ui.sector_from_units.setEnabled(_status_sector)
        self.ui.sector_to_label.setEnabled(_status_sector)
        self.ui.sector_to_value.setEnabled(_status_sector)
        self.ui.sector_to_units.setEnabled(_status_sector)
        self.sector_changed()

    def init_statusbar(self):
        self.eventProgress = QtGui.QProgressBar(self.ui.statusbar)
        self.eventProgress.setMinimumSize(20, 14)
        self.eventProgress.setMaximumSize(540, 100)
        self.eventProgress.setVisible(False)
        self.ui.statusbar.addPermanentWidget(self.eventProgress)

    def get_image_dimension(self, array_image):
        if len(np.shape(array_image)) > 2:
            return np.shape(array_image[0])
        else:
            return np.shape(array_image)

    def get_selected_image(self, file_index):

        if len(np.shape(self.working_data)) > 2:
            return self.working_data[file_index]
        else:
            return self.working_data

    def display_grid(self):
        [width, height] = self.get_image_dimension(self.working_data)
        # bin_size = float(str(self.ui.lineEdit.text()))
        bin_size = self.ui.grid_size_slider.value()
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

        line_color = (self.guide_color_slider['red'],
                      self.guide_color_slider['green'],
                      self.guide_color_slider['blue'],
                      self.guide_color_slider['alpha'], 0.5)
        lines = np.array([line_color for n in np.arange(len(pos))],
                         dtype=[('red', np.ubyte), ('green', np.ubyte),
                                ('blue', np.ubyte), ('alpha', np.ubyte),
                                ('width', float)])

        line_view_binning = pg.GraphItem()
        self.ui.image_view.addItem(line_view_binning)
        line_view_binning.setData(pos=pos,
                                  adj=adj,
                                  pen=lines,
                                  symbol=None,
                                  pxMode=False)

        self.line_view_binning = line_view_binning

    def sector_changed(self):
        self.circle_center_changed()

    def grid_size_changed(self):
        self.ui.image_view.removeItem(self.line_view_binning)
        self.display_grid()

    def calculate_corners_angles(self):
        '''top vertical being angle 0'''

        x0 = float(str(self.ui.circle_x.text()))
        y0 = float(str(self.ui.circle_y.text()))

        width = self.width
        height = self.height
        #        width = self.height
        #        height = self.width

        theta_tr = np.NaN  # angle top right
        theta_br = np.NaN  # bottom right
        theta_bl = np.NaN  # bottom left
        theta_tl = np.NaN  # top left

        theta_tr = np.arctan((width - x0) / y0)
        theta_tr_deg = np.rad2deg(theta_tr)

        theta_br = np.pi - np.arctan((width - x0) / (height - y0))
        theta_br_deg = np.rad2deg(theta_br)

        theta_bl = np.pi + np.arctan(x0 / (height - y0))
        theta_bl_deg = np.rad2deg(theta_bl)

        theta_tl = 2 * np.pi - np.arctan(x0 / y0)
        theta_tl_deg = np.rad2deg(theta_tl)

        self.corners['top_right'] = theta_tr_deg
        self.corners['bottom_right'] = theta_br_deg
        self.corners['bottom_left'] = theta_bl_deg
        self.corners['top_left'] = theta_tl_deg

    def calculate_sector_xy_position(self, angle=0, x0=0, y0=0):

        x = np.NaN
        y = np.NaN

        angle_top_right = self.corners['top_right']
        angle_bottom_right = self.corners['bottom_right']
        angle_bottom_left = self.corners['bottom_left']
        angle_top_left = self.corners['top_left']

        # print("angle_top_right: {}".format(angle_top_right))
        # print("angle_bottom_right: {}".format(angle_bottom_right))
        # print("angle_bottom_left: {}".format(angle_bottom_left))
        # print("angle_top_left: {}".format(angle_top_left))

        if (angle_top_right <= angle) and \
                (angle <= angle_bottom_right):
            # right

            # get x
            x = self.height

            # get y
            _angle = np.abs(90 - angle)

            if angle == 90:
                y = 0
            else:
                angle_rad = np.deg2rad(_angle)
                y = np.tan(angle_rad) * (self.height - x0)

            if angle <= 90:
                y = y0 - y
            else:
                y = y0 + y

        elif angle_bottom_right < angle < angle_bottom_left:
            # bottom

            # get y
            y = self.width

            # get x
            _angle = np.abs(180 - angle)

            if angle == 180:
                x = 0
            else:
                angle_rad = np.deg2rad(_angle)
                x = (y - y0) * np.tan(angle_rad)

            if angle <= 180:
                x = x0 + x
            else:
                x = x0 - x

        elif angle_bottom_left <= angle <= angle_top_left:
            # left

            # get x
            x = 0

            # get y
            _angle = np.abs(270 - angle)

            if angle == 270:
                y = 0
            else:
                angle_rad = np.deg2rad(_angle)
                y = np.tan(angle_rad) * x0

            if angle <= 270:
                y = y0 + y
            else:
                y = y0 - y

        else:
            # top

            # get y
            y = 0

            # get x
            b_right_part = True
            if angle > angle_top_left:
                angle = np.abs(360 - angle)
                b_right_part = False

            if angle == 0:
                x = 0
            else:
                angle_rad = np.deg2rad(angle)
                x = y0 * np.tan(angle_rad)

            if b_right_part:
                x = x0 + x
            else:
                x = x0 - x

        return [y, x]

    def manual_circle_center_changed(self):
        new_x0 = np.int(self.vLine.value())
        self.ui.circle_x.setText("{}".format(new_x0))

        new_y0 = np.int(self.hLine.value())
        self.ui.circle_y.setText("{}".format(new_y0))

        self.circle_center_changed()

    def circle_center_changed(self):

        if self.ui.sector_full_circle.isChecked():
            if self.sector_g:
                self.ui.image_view.removeItem(self.sector_g)
            return

        x0 = float(str(self.ui.circle_x.text()))
        y0 = float(str(self.ui.circle_y.text()))
        from_angle = float(str(self.ui.sector_from_value.text()))
        to_angle = float(str(self.ui.sector_to_value.text()))

        self.calculate_corners_angles()
        self.update_angle_label_position()

        [y1, x1] = self.calculate_sector_xy_position(angle=from_angle, x0=x0, y0=y0)
        [y2, x2] = self.calculate_sector_xy_position(angle=to_angle, x0=x0, y0=y0)

        pos = np.array([[x0, y0], [x1, y1], [x2, y2]])
        adj = np.array([[0, 1], [1, 2], [2, 0]])

        symbols = ['+', 'o', 'o']

        lines = np.array([(255, 0, 0, 255, 2), (255, 0, 0, 0, 1), (255, 0, 0, 255, 2)],
                         dtype=[('red', np.ubyte), ('green', np.ubyte), ('blue', np.ubyte), ('alpha', np.ubyte),
                                ('width', float)])

        if self.sector_g:
            self.ui.image_view.removeItem(self.sector_g)
        self.sector_g = pg.GraphItem()
        self.ui.image_view.addItem(self.sector_g)
        self.sector_g.setData(pos=pos, adj=adj, pen=lines, size=1, symbol=symbols, pxMode=False)

    def guide_color_changed(self, index):
        red = self.ui.guide_red_slider.value()
        green = self.ui.guide_green_slider.value()
        blue = self.ui.guide_blue_slider.value()
        alpha = self.ui.guide_alpha_slider.value()
        self.guide_color_slider['red'] = red
        self.guide_color_slider['green'] = green
        self.guide_color_slider['blue'] = blue
        self.guide_color_slider['alpha'] = alpha
        self.circle_center_changed()

        self.ui.image_view.removeItem(self.line_view_binning)
        self.display_grid()

    def apply_clicked(self):
        _center = {}
        _center['x0'] = np.float(str(self.ui.circle_x.text()))
        _center['y0'] = np.float(str(self.ui.circle_y.text()))
        self.center = _center

        _angle_range = {}
        if self.ui.sector_full_circle.isChecked():
            _from_angle = 0
            _to_angle = 360
        else:
            _from_angle = np.float(str(self.ui.sector_from_value.text()))
            _to_angle = np.float(str(self.ui.sector_to_value.text()))
        _angle_range['from'] = _from_angle
        _angle_range['to'] = _to_angle
        self.angle_range = _angle_range

        self.close()

    def cancel_clicked(self):
        self.close()

    def file_index_changed(self):
        file_index = self.ui.slider.value()
        live_image = self.get_selected_image(file_index)

        _view = self.ui.image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()

        first_update = False
        if self.histogram_level == []:
            first_update = True
        _histo_widget = self.ui.image_view.getHistogramWidget()
        self.histogram_level = _histo_widget.getLevels()

        _image = np.transpose(live_image)
        self.ui.image_view.setImage(_image)
        self.live_image = _image
        _view_box.setState(_state)

        if not first_update:
            _histo_widget.setLevels(self.histogram_level[0], self.histogram_level[1])


    def display_image(self, image):
        image = np.transpose(image)
        self.ui.image_view.setImage(image)

    def closeEvent(self, eventhere=None):
        print("Leaving Parameters Selection UI")



