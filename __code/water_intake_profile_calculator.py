import ipywe.fileselector

from IPython.core.display import HTML
from IPython.core.display import display
from ipywidgets import widgets
from ipywidgets.widgets import interact

import matplotlib.pyplot as plt
import numpy as np
import os
import re
import re
import pandas as pd

import matplotlib.gridspec as gridspec
import pytz
import datetime

import pyqtgraph as pg
from pyqtgraph.dockarea import *

from __code.file_handler import make_ascii_file

try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtGui import QMainWindow
except ImportError:
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtWidgets import QApplication, QMainWindow

from NeuNorm.normalization import Normalization

from __code.metadata_handler import MetadataHandler
from __code.file_handler import retrieve_time_stamp
from __code import file_handler

from __code.ui_water_intake_profile  import Ui_MainWindow as UiMainWindow


class MeanRangeCalculation(object):
    '''
    Mean value of all the counts between left_pixel and right pixel
    '''

    def __init__(self, data=None):
        self.data = data
        self.nbr_pixel = len(self.data)

    def calculate_left_right_mean(self, pixel=-1):
        _data = self.data
        _nbr_pixel = self.nbr_pixel

        self.left_mean = np.mean(_data[0:pixel+1])
        self.right_mean = np.mean(_data[pixel+1:_nbr_pixel])

    def calculate_delta_mean_square(self):
        self.delta_square = np.square(self.left_mean - self.right_mean)


class WaterIntakeHandler(object):
    """This class calculates the water intake position of a set of profiles"""

    dict_profiles = {}   # {'0': {'data': [], 'delta_time': 45455}, '1': {...} ...}

    def __init__(self, dict_profiles={}):
        self.dict_profiles = dict_profiles
        self.calculate()

    def calculate(self):
        _dict_profiles = self.dict_profiles
        nbr_pixels = len(_dict_profiles['1']['data'])
        nbr_files = len(_dict_profiles.keys())

        water_intake_deltatime = []
        water_intake_peak = []
        for _index_file in np.arange(1, nbr_files):
            _profile = _dict_profiles[str(_index_file)]
            _profile_data = _profile['data']
            _delta_time = _profile['delta_time']
            delta_array = []
            for _pixel in np.arange(0, nbr_pixels-1):
                _o_range = MeanRangeCalculation(data=_profile_data)
                _o_range.calculate_left_right_mean(pixel=_pixel)
                _o_range.calculate_delta_mean_square()
                delta_array.append(_o_range.delta_square)

            peak_value = delta_array.index(max(delta_array[0: nbr_pixels -5]))
            water_intake_peak.append(peak_value)
            water_intake_deltatime.append(_delta_time)

        self.water_intake_peak = water_intake_peak
        self.water_intake_deltatime = water_intake_deltatime


class WaterIntakeProfileSelector(QMainWindow):

    list_data = []

    dict_data = {}
    dict_data_raw = {} # dict data untouched (not sorted)
    list_images_raw = [] # use to reste dict_data

    current_image = []
    ignore_first_image_checked = True
    roi_width = 0.01
    roi = {'x0': 0, 'y0': 0, 'width': 200, 'height': 200}
    table_column_width = [350, 150, 200]
    dict_profiles = {} # contain all the profiles just before calculating the water intake

    def __init__(self, parent=None, dict_data={}):

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
            (maybe hidden behind this browser!)</span>'))

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Profile Selector")

        self.dict_data_raw = dict_data
        self.dict_data = dict_data
        self.list_data = dict_data['list_data'][1:]
        self.list_images_raw = dict_data['list_images']

        self.init_statusbar()
        self._init_pyqtgraph()
        self._init_widgets()
        self.sort_dict_data()
        self.update_image()
        self.update_plots()
        self.update_infos_tab()

    def init_statusbar(self):

        _width_labels = 40
        _height_labels = 30

        # x0, y0, width and height of selection
        roi_label = QtGui.QLabel("ROI selected:  ")
        _x0_label = QtGui.QLabel("X0:")
        self.x0_value = QtGui.QLabel("0")
        self.x0_value.setFixedSize(_width_labels, _height_labels)
        _y0_label = QtGui.QLabel("Y0:")
        self.y0_value = QtGui.QLabel("0")
        self.y0_value.setFixedSize(_width_labels, _height_labels)
        _width_label = QtGui.QLabel("Width:")
        self.width_value = QtGui.QLabel("20")
        self.width_value.setFixedSize(_width_labels, _height_labels)
        _height_label = QtGui.QLabel("Height:")
        self.height_value = QtGui.QLabel("20")
        self.height_value.setFixedSize(_width_labels, _height_labels)

        hori_layout = QtGui.QHBoxLayout()
        hori_layout.addWidget(roi_label)
        hori_layout.addWidget(_x0_label)
        hori_layout.addWidget(self.x0_value)
        hori_layout.addWidget(_y0_label)
        hori_layout.addWidget(self.y0_value)
        hori_layout.addWidget(_width_label)
        hori_layout.addWidget(self.width_value)
        hori_layout.addWidget(_height_label)
        hori_layout.addWidget(self.height_value)

        # spacer
        spacerItem = QtGui.QSpacerItem(22520, 40, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        hori_layout.addItem(spacerItem)

        # progress bar
        self.eventProgress = QtGui.QProgressBar(self.ui.statusbar)
        self.eventProgress.setMinimumSize(300, 20)
        self.eventProgress.setMaximumSize(300, 20)
        self.eventProgress.setVisible(False)
        hori_layout.addWidget(self.eventProgress)
        self.setStyleSheet("QStatusBar{padding-left:8px;color:red;font-weight:bold;}")

        # add status bar in main ui
        bottom_widget = QtGui.QWidget()
        bottom_widget.setLayout(hori_layout)
        self.ui.statusbar.addPermanentWidget(bottom_widget)

    def sort_dict_data(self):
        pass

    def _init_pyqtgraph(self):
        area = DockArea()
        area.setVisible(True)
        d1 = Dock("Sample Image", size=(200, 300))
        d2 = Dock("Profile", size=(200, 100))
        d3 = Dock("Water Intake", size=(200, 400))

        area.addDock(d1, 'top')
        area.addDock(d2, 'bottom')
        area.addDock(d3, 'right')

        # image view
        self.ui.image_view = pg.ImageView()
        self.ui.image_view.ui.menuBtn.hide()
        self.ui.image_view.ui.roiBtn.hide()

        _color = QtGui.QColor(62, 13, 244)
        _pen = QtGui.QPen()
        _pen.setColor(_color)
        _pen.setWidthF(self.roi_width)
        _x0 = self.roi['x0']
        _y0 = self.roi['y0']
        _width = self.roi['width']
        _height = self.roi['height']
        _roi_id = pg.ROI([_x0, _y0], [_width, _height], pen=_pen, scaleSnap=True)
        _roi_id.addScaleHandle([1, 1], [0, 0])
        _roi_id.addScaleHandle([0, 0], [1, 1])
        self.ui.image_view.addItem(_roi_id)
        _roi_id.sigRegionChanged.connect(self.roi_moved)
        self.roi_id = _roi_id
        d1.addWidget(self.ui.image_view)

        # profile
        self.profile = pg.PlotWidget(title='Profile')
        self.profile.plot()
        d2.addWidget(self.profile)

        # water intake
        self.water_intake = pg.PlotWidget(title='Water Intake')
        self.water_intake.plot()
        self.ui.water_intake_refresh_button = QtGui.QPushButton("Refresh Water Intake Plot")
        self.ui.water_intake_refresh_button.clicked.connect(self.refresh_water_intake_plot_clicked)
        vertical_layout = QtGui.QVBoxLayout()
        vertical_layout.addWidget(self.water_intake)
        vertical_layout.addWidget(self.ui.water_intake_refresh_button)
        wi_widget = QtGui.QWidget()
        wi_widget.setLayout(vertical_layout)
        d3.addWidget(wi_widget)

        # set up layout
        vertical_layout = QtGui.QVBoxLayout()
        vertical_layout.addWidget(area)
        self.ui.widget.setLayout(vertical_layout)

    def _init_widgets(self):
        nbr_files = len(self.list_data)
        self.ui.file_index_slider.setMaximum(nbr_files)
        self.ui.file_index_slider.setMinimum(2)
        self.ui.file_index_slider.setValue(2)
        self.update_labels()

        # update size of table columns
        nbr_columns = self.ui.tableWidget.columnCount()
        for _col in range(nbr_columns):
            self.ui.tableWidget.setColumnWidth(_col, self.table_column_width[_col])

    def update_infos_tab(self):
        dict_data = self.dict_data

        list_files = dict_data['list_images']
        list_time_stamp = dict_data['list_time_stamp']
        list_time_stamp_user = dict_data['list_time_stamp_user_format']

        for _row, _file_name in enumerate(list_files):
            _short_name = os.path.basename(_file_name)
            _time_stamp_unix = list_time_stamp[_row]
            _time_stamp_user = list_time_stamp_user[_row]

            self.__insert_information_in_table(row=_row,
                                               col0=_short_name,
                                               col1=_time_stamp_unix,
                                               col2=_time_stamp_user)

    def __insert_information_in_table(self, row, col0, col1, col2):
        self.ui.tableWidget.insertRow(row)

        #col0
        _item = QtGui.QTableWidgetItem(str(str(col0)))
        self.ui.tableWidget.setItem(row, 0, _item)

        #col1
        _item = QtGui.QTableWidgetItem(str(str(col1)))
        self.ui.tableWidget.setItem(row, 1, _item)

        # col2
        _item = QtGui.QTableWidgetItem(str(str(col2)))
        self.ui.tableWidget.setItem(row, 2, _item)

    def update_labels(self):
        _roi = self.roi
        _x0 = _roi['x0']
        _y0 = _roi['y0']
        _width = _roi['width']
        _height = _roi['height']
        self.x0_value.setText(str(_x0))
        self.y0_value.setText(str(_y0))
        self.width_value.setText(str(_width))
        self.height_value.setText(str(_height))

    def refresh_water_intake_plot_clicked(self):
        self.update_water_intake_plot()

    def update_plots(self):
        self.update_profile_plot()
        self.update_water_intake_plot()

    def update_profile_plot(self):
        _image = self.current_image
        _roi = self.roi

        x0 = _roi['x0']
        y0 = _roi['y0']
        width = _roi['width']
        height = _roi['height']

        x1 = x0 + width
        y1 = y0 + height

        _image_of_roi = _image[y0:y1, x0:x1]
        _profile_algo = self.get_profile_algo()
        if _profile_algo == 'add':
            _profile = np.sum(_image_of_roi, axis=1)
        elif _profile_algo == 'mean':
            _profile = np.mean(_image_of_roi, axis=1)
        elif _profile_algo == 'median':
            _profile = np.median(_image_of_roi, axis=1)
        else:
            _profile = []
        self.profile.clear()
        self.profile.plot(_profile)
        self.profile.setLabel('left', 'Counts')
        self.profile.setLabel('bottom', 'Y pixels')

    def get_profile_algo(self):
        if self.ui.add_radioButton.isChecked():
            return 'add'
        elif self.ui.mean_radioButton.isChecked():
            return 'mean'
        elif self.ui.median_radioButton.isChecked():
            return 'median'
        return ''

    def update_water_intake_plot(self):
        self.calculate_all_profiles()
        o_water_intake_handler = WaterIntakeHandler(dict_profiles=self.dict_profiles)
        delta_time = o_water_intake_handler.water_intake_deltatime
        peak = o_water_intake_handler.water_intake_peak

        self.water_intake.plot(delta_time, peak)
        self.water_intake.setLabel('left', 'Counts')
        self.water_intake.setLabel('bottom', 'Delta Time')

    def calculate_all_profiles(self):
        dict_data = self.dict_data

        _roi = self.roi

        x0 = _roi['x0']
        y0 = _roi['y0']
        width = _roi['width']
        height = _roi['height']

        x1 = x0 + width
        y1 = y0 + height

        list_images = dict_data['list_images']
        list_time_stamp = dict_data['list_time_stamp']
        list_data = dict_data['list_data']
        list_time_stamp_user_format = dict_data['list_time_stamp_user_format']
        _algo_used = self.get_profile_algo()

        time_stamp_first_file = float(list_time_stamp[0])

        nbr_images = len(list_images)
        dict_profiles = {}
        for index in np.arange(1, nbr_images):
            _image = list_data[index]
            _image_of_roi = _image[y0:y1, x0:x1]
            if _algo_used == 'add':
                _profile = np.sum(_image_of_roi, axis=1)
            elif _algo_used == 'mean':
                _profile = np.mean(_image_of_roi, axis=1)
            elif _algo_used == 'median':
                _profile = np.median(_image_of_roi, axis=1)
            else:
                raise NotImplementedError

            time_stamp = float(list_time_stamp[index])
            delta_time = time_stamp - time_stamp_first_file

            dict_profiles[str(index)] = {'data': _profile,
                                         'delta_time': delta_time}
        self.dict_profiles = dict_profiles

    def export_profile_clicked(self):
        #select output folder
        _export_folder = QFileDialog.getExistingDirectory(self, caption = "Select Output Folder",
                                                         options=QFileDialog.ShowDirsOnly)
        export_folder = os.path.abspath(_export_folder)

        dict_data = self.dict_data
        list_images = dict_data['list_images']
        list_time_stamp = dict_data['list_time_stamp']
        list_data = dict_data['list_data']
        list_time_stamp_user_format = dict_data['list_time_stamp_user_format']
        _algo_used = self.get_profile_algo()

        # get metadata roi selection
        _roi = self.roi
        x0 = _roi['x0']
        y0 = _roi['y0']
        width = _roi['width']
        height = _roi['height']
        x1 = x0 + width
        y1 = y0 + height

        input_folder = os.path.dirname(list_images[0])

        nbr_images = len(list_images)
        self.eventProgress.setMinimum(1)
        self.eventProgress.setMaximum(nbr_images)
        self.eventProgress.setValue(1)
        self.eventProgress.setVisible(True)

        for index in np.arange(1, nbr_images):
            _short_file_name = os.path.basename(list_images[index])
            [_basename, _] = os.path.splitext(_short_file_name)
            output_file_name = os.path.join(export_folder, _basename + '_profile.txt')

            metadata = []
            metadata.append("# roi [x0, y0, width, height]: [{}, {}, {}, {}]".format(x0, y0, width, height))
            metadata.append("# Profile over ROI selected integrated along x-axis")
            metadata.append("# folder: {}".format(input_folder))
            metadata.append("# filename: {}".format(_short_file_name))
            metadata.append("# timestamp (unix): {}".format(list_time_stamp[index]))
            metadata.append("# timestamp (user format): {}".format(list_time_stamp_user_format[index]))
            metadata.append("# algorithm used: {}".format(_algo_used))
            metadata.append("# ")
            metadata.append("# pixel, counts")

            _image = list_data[index]
            _image_of_roi = _image[y0:y1, x0:x1]
            if _algo_used == 'add':
                _profile = np.sum(_image_of_roi, axis=1)
            elif _algo_used == 'mean':
                _profile = np.mean(_image_of_roi, axis=1)
            elif _algo_used == 'median':
                _profile = np.median(_image_of_roi, axis=1)
            else:
                raise NotImplementedError

            data = []
            for _pixel_index, _counts in enumerate(_profile):
                _line = "{}, {}".format(_pixel_index+y0, _counts)
                data.append(_line)

            make_ascii_file(metadata=metadata, data=data, output_file_name=output_file_name, dim='1d')
            self.eventProgress.setValue(index)

        self.eventProgress.setVisible(False)

    def export_water_intake_clicked(self):
        pass

    def roi_moved(self):
        region = self.roi_id.getArraySlice(self.current_image, self.ui.image_view.imageItem)

        x0 = region[0][0].start
        x1 = region[0][0].stop
        y0 = region[0][1].start
        y1 = region[0][1].stop

        width = np.abs(x1-x0)
        height = np.abs(y1-y0)
        self.roi['x0'] = x0
        self.roi['y0'] = y0
        self.roi['width'] = width-1
        self.roi['height'] = height-1
        self.update_labels()
        self.update_profile_plot()

    def _clean_image(self, image):
        _result_inf = np.where(np.isinf(image))
        image[_result_inf] = np.NaN
        return image

    def _force_range(self, image):
        range_max = 1.2
        _result_range = np.where(image > range_max)
        image[_result_range] = np.NaN
        return image

    def update_image(self):
        index_selected = self.ui.file_index_slider.value()
        _image = self.list_data[index_selected-1]
        _image = np.transpose(_image)
        _image = self._clean_image(_image)
        _image = self._force_range(_image)
        self.current_image = _image
        self.ui.image_view.setImage(_image)

    def slider_changed(self, value):
        self.ui.file_index_value.setText(str(value))
        self.update_image()
        self.update_profile_plot()

    # files sorting
    def sorting_files_checkbox_clicked(self):
        is_sorting_by_name = self.ui.sort_files_by_name_radioButton.isChecked()
        self.ui.time_between_runs_label.setEnabled(is_sorting_by_name)
        self.ui.time_between_runs_spinBox.setEnabled(is_sorting_by_name)
        self.ui.time_between_runs_units_label.setEnabled(is_sorting_by_name)
        self.__sort_files(is_by_name=is_sorting_by_name)
        self.update_infos_tab()

    def __sort_files(self, is_by_name=True):
        # reformat name to make sure the last digit have 4 digits
        if is_by_name:
            self._fix_index_of_files()
        else:
            self._reset_list_of_files()

    def _reset_list_of_files(self):
        list_images_raw = self.list_images_raw
        self.dict_data_raw['list_images'] = list_images_raw

    def _fix_index_of_files(self):
        """reformat file name to make sure index has 4 digits
        """
        _dict_data_raw = self.dict_data_raw
        list_files = _dict_data_raw['list_images']
        formated_list_files = []

        re_string = r"^(?P<part1>\w*)_(?P<index>\d+)$"
        for _file in list_files:
            dirname = os.path.dirname(_file)
            basename = os.path.basename(_file)
            [base, ext] = os.path.splitext(basename)
            m = re.match(re_string, base)
            if m is None:
                raise ValueError
            else:
                part1 = m.group('part1')
                index = np.int(m.group('index'))
                new_index = "{:04d}".format(index)
                new_file = os.path.join(dirname, part1 + '_' + new_index + ext)
                formated_list_files.append(new_file)

        self.dict_data['list_images'] = formated_list_files


    def time_between_runs_spinBox_changed(self):
        pass

    def profile_algo_changed(self):
        self.update_profile_plot()

    def help_button_clicked(self):
        import webbrowser
        webbrowser.open("http://localhost:1313/en/tutorial/notebooks/water_intake_profile_calculator/")

    def ok_button_clicked(self):
        # do soemthing here
        self.close()

    def cancel_button_clicked(self):
        self.close()


class WaterIntakeProfileCalculator(object):

    dict_files = {'list_images': [],   # list of full file name images
                  'list_data': [],
                  'list_time_stamp': [],
                  'list_time_stamp_user_format': [],
                  }

    def __init__(self, working_dir='./'):
        self.working_dir = working_dir

    def select_file_help(self, value):
        import webbrowser
        webbrowser.open("https://neutronimaging.pages.ornl.gov/en/tutorial/notebooks/file_selector/#select_profile")

    def select_data(self):
        help_ui = widgets.Button(description="HELP",
                                 button_style='info')
        help_ui.on_click(self.select_file_help)
        display(help_ui)

        self.files_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select Images ...',
                                                             start_dir=self.working_dir,
                                                             next=self.load,
                                                             multiple=True)

        self.files_ui.show()

    def load(self, list_images):
        # list_images = self.files_ui.selected
        self.dict_files = retrieve_time_stamp(list_images)
        #self.__sort_files_using_time_stamp(self.dict_files)
        self.__load_files()

    # Helper functions
    def __load_files(self):
        o_load = Normalization()
        o_load.load(file=self.dict_files['list_images'], notebook=True)
        self.dict_files['list_data'] = o_load.data['sample']['data']

    def __sort_files_using_time_stamp(self, dict_time_stamp):
        """Using the time stamp information, all the files will be sorted in ascending order of time stamp"""

        list_images = dict_time_stamp['list_images']
        list_time_stamp = dict_time_stamp['list_time_stamp']
        list_time_stamp_user_format = dict_time_stamp['list_time_stamp_user_format']

        list_images = np.array(list_images)
        time_stamp = np.array(list_time_stamp)
        time_stamp_user_format = np.array(list_time_stamp_user_format)

        # sort according to time_stamp array
        sort_index = np.argsort(time_stamp)

        # using same sorting index of the other list
        sorted_list_images = list_images[sort_index]
        sorted_list_time_stamp = time_stamp[sort_index]
        sorted_list_time_stamp_user_format = time_stamp_user_format[sort_index]

        self.dict_files = {'list_images': list(sorted_list_images),
                           'list_time_stamp': sorted_list_time_stamp,
                           'list_time_stamp_user_format': sorted_list_time_stamp_user_format}












