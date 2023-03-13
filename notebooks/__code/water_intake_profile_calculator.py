from IPython.core.display import HTML
from IPython.core.display import display
from ipywidgets import widgets

import numpy as np
import os
import re
import glob
from scipy.special import erf
from scipy.optimize import curve_fit
from changepy import pelt
from changepy.costs import normal_var

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

from __code.file_handler import make_ascii_file
from __code.ipywe import fileselector
from __code.file_handler import retrieve_time_stamp
from __code.file_format_reader import DscReader
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

        self.left_mean = np.nanmean(_data[0:pixel+1])
        self.right_mean = np.nanmean(_data[pixel+1:_nbr_pixel])

    def calculate_delta_mean_square(self):
        self.delta_square = np.square(self.left_mean - self.right_mean)


class WaterIntakeHandler(object):
    """This class calculates the water intake position of a set of profiles"""

    dict_profiles = {}   # {'0': {'data': [], 'delta_time': 45455}, '1': {...} ...}

    water_intake_peak_sliding_average = []
    water_intake_peak_erf = []
    water_intake_deltatime = []

    dict_error_function_parameters = {}

    # fitting by error function requires that the signal goes from max to min values
    is_data_from_max_to_min = True

    def __init__(self, dict_profiles={}, ignore_first_image=True, algorithm_selected='sliding_average'):
        self.dict_profiles = dict_profiles
        self.ignore_first_image = ignore_first_image

        if algorithm_selected == 'sliding_average':
            self.calculate_using_sliding_average()
        elif algorithm_selected == 'error_function':
            self.calculate_using_erf()
        elif algorithm_selected == 'change_point':
            self.calculate_change_point()
        else:
            raise ValueError("algorithm not implemented yet!")

    @staticmethod
    def fitting_function(x, c, w, m, n):
        return ((m-n)/2.) * erf((x-c)/w) + (m+n)/2.

    def are_data_from_max_to_min(self, ydata):
        nbr_points = len(ydata)
        nbr_point_for_investigation = int(nbr_points * 0.1)

        mean_first_part = np.mean(ydata[0:nbr_point_for_investigation])

        ydata = ydata.copy()
        ydata_reversed = ydata[::-1]
        mean_last_part = np.mean(ydata_reversed[0: nbr_point_for_investigation])

        if mean_first_part > mean_last_part:
            return True
        else:
            return False

    def calculate_change_point(self):
        _dict_profiles = self.dict_profiles
        nbr_files = len(_dict_profiles.keys())

        if self.ignore_first_image:
            _start_file = 1
            _end_file = nbr_files+1
        else:
            _start_file = 0
            _end_file = nbr_files

        water_intake_peaks = []
        water_intake_deltatime = []
        for _index_file in np.arange(_start_file, _end_file):
            _profile = _dict_profiles[str(_index_file)]
            ydata = _profile['data']
            xdata = _profile['delta_time']

            var = np.mean(ydata)
            result = pelt(normal_var(ydata, var), len(ydata))
            if len(result) > 2:
                peak = np.mean(result[2:])
            else:
                peak = np.mean(result[1:])
            water_intake_peaks.append(peak)
            water_intake_deltatime.append(xdata)

        self.water_intake_peaks_change_point = water_intake_peaks
        self.water_intake_deltatime = water_intake_deltatime

    def calculate_using_erf(self):
        _dict_profiles = self.dict_profiles
        nbr_files = len(_dict_profiles.keys())

        if self.ignore_first_image:
            _start_file = 1
            _end_file = nbr_files + 1
        else:
            _start_file = 0
            _end_file = nbr_files

        dict_error_function_parameters = dict()
        water_intake_peaks_erf = []
        water_intake_peaks_erf_error = []
        delta_time = []

        for _index_file in np.arange(_start_file, _end_file):
            _profile = _dict_profiles[str(_index_file)]
            ydata = _profile['data']
            xdata = _profile['delta_time']

            is_data_from_max_to_min = self.are_data_from_max_to_min(ydata)
            self.is_data_from_max_to_min = is_data_from_max_to_min
            if not is_data_from_max_to_min:
                ydata = ydata[::-1]

            (popt, pcov) = self.fitting_algorithm(ydata)

            _local_dict = {'c': popt[0],
                           'w': popt[1],
                           'm': popt[2],
                           'n': popt[3]}

            error = np.sqrt(np.diag(pcov))
            _peak = int(popt[0] + (popt[1]/np.sqrt(2)))
            water_intake_peaks_erf.append(_peak)

            for _i, _err in enumerate(error):
                if np.isnan(_err):
                    error[_i] = np.sqrt(popt[0])
                elif np.isinf(_err):
                    error[_i] = np.sqrt(popt[0])
                else:
                    error[_i] = _err

            _peak_error = int(error[0] + (error[1]/np.sqrt(2)))

            water_intake_peaks_erf_error.append(_peak_error)
            delta_time.append(xdata)

            dict_error_function_parameters[str(_index_file)] = _local_dict

        self.water_intake_peaks_erf = water_intake_peaks_erf
        self.dict_error_function_parameters = dict_error_function_parameters
        self.dict_error_function_parameters_error = water_intake_peaks_erf_error
        self.water_intake_deltatime = delta_time

    def fitting_algorithm(self, ydata):
        fitting_xdata = np.arange(len(ydata))
        popt, pcov = curve_fit(self.fitting_function, fitting_xdata, ydata, maxfev=3000)
        return (popt, pcov)

    def calculate_using_sliding_average(self):
        _dict_profiles = self.dict_profiles
        nbr_pixels = len(_dict_profiles['1']['data'])
        nbr_files = len(_dict_profiles.keys())

        if self.ignore_first_image:
            _start_file = 1
            _end_file = nbr_files+1
        else:
            _start_file = 0
            _end_file = nbr_files

        water_intake_deltatime = []
        water_intake_peak = []
        for _index_file in np.arange(_start_file, _end_file):
            _profile = _dict_profiles[str(_index_file)]
            _profile_data = _profile['data']
            _delta_time = _profile['delta_time']
            delta_array = []
            _o_range = MeanRangeCalculation(data=_profile_data)
            for _pixel in np.arange(0, nbr_pixels-5):
                _o_range.calculate_left_right_mean(pixel=_pixel)
                _o_range.calculate_delta_mean_square()
                delta_array.append(_o_range.delta_square)

            peak_value = delta_array.index(max(delta_array[0: nbr_pixels -5]))
            water_intake_peak.append(peak_value)
            water_intake_deltatime.append(_delta_time)

        self.water_intake_peak_sliding_average = water_intake_peak
        self.water_intake_deltatime = water_intake_deltatime


class WaterIntakeProfileSelector(QMainWindow):

    list_data = []

    dict_data = {}
    dict_data_raw = {} # dict data untouched (not sorted)
    list_images_raw = [] # use to reste dict_data
    dict_water_intake = {}
    dic_disc = {} # dictionary created when loading dsc folder

    current_image = []
    ignore_first_image_checked = True
    roi_width = 0.05
    roi = {'x0': 88, 'y0': 131, 'width': 142, 'height': 171}
    table_column_width = [350, 150, 200]
    dict_profiles = {} # contain all the profiles just before calculating the water intake

    # by default, we integrate over the x-axis
    is_inte_along_x_axis = True

    histogram_level = []

    # array of water intake values
    water_intake_peaks = []
    water_intake_peaks_erf = []
    water_intake_peak_change_point = []

    # state of the image
    image_view_state = {}

    algorithm_selected = 'sliding_average'

    def __init__(self, parent=None, dict_data={}):

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that popped up \
            (maybe hidden behind this browser!)</span>'))

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Water Intake Calculator")

        self.dict_data_raw = dict_data.copy()
        self.dict_data = dict_data.copy()
        self.list_data = dict_data['list_data'].copy()
        self.list_images_raw = dict_data['list_images']
        self.working_dir = os.path.dirname(self.list_images_raw[0])

        self.init_statusbar()
        self._init_pyqtgraph()
        self._init_widgets()
        self.sort_dict_data()
        self.update_water_intake_plot()
        self.update_profile_plot_water_intake_peak()
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
        self.sorting_files_checkbox_clicked()

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
        self.ui.image_view = pg.ImageView(view=pg.PlotItem())

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
        self.profile_vline = pg.InfiniteLine(angle=90, movable=False)
        self.profile.addItem(self.profile_vline, ignoreBounds=True)
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

        # add progress bar
        label = QtGui.QLabel("File Index:")
        label.setMinimumSize(QtCore.QSize(60, 30))
        label.setMaximumSize(QtCore.QSize(60, 30))
        hori_layout = QtGui.QHBoxLayout()
        self.ui.file_index_slider = QtGui.QSlider()
        self.ui.file_index_slider.setMinimumSize(QtCore.QSize(400, 40))
        self.ui.file_index_slider.setMaximumSize(QtCore.QSize(40, 40))
        self.ui.file_index_slider.setOrientation(QtCore.Qt.Horizontal)
        self.ui.file_index_slider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.ui.file_index_slider.setTickInterval(1)

        self.ui.file_index_slider.valueChanged['int'].connect(self.slider_changed)
        self.ui.file_index_value = QtGui.QLabel()
        self.ui.file_index_value.setMinimumSize(QtCore.QSize(40, 30))
        self.ui.file_index_value.setMaximumSize(QtCore.QSize(40, 30))

        spacerItem3 = QtGui.QSpacerItem(408, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)

        hori_layout.addWidget(label)
        hori_layout.addWidget(self.ui.file_index_slider)
        hori_layout.addWidget(self.ui.file_index_value)
        hori_layout.addItem(spacerItem3)
        bottom_widget = QtGui.QWidget()
        bottom_widget.setLayout(hori_layout)
        vertical_layout.addWidget(bottom_widget)

        self.ui.widget.setLayout(vertical_layout)

    def _init_widgets(self, ignore_first_image=True, first_init=True):
        self.ui.file_index_slider.blockSignals(True)

        nbr_files = len(self.list_data)
        self.ui.file_index_slider.setMaximum(nbr_files)

        if ignore_first_image:
            _min = 2
        else:
            _min = 1

        if first_init:
            _value = _min
        else:
            _value = self.ui.file_index_slider.value()

        self.ui.file_index_slider.setMinimum(_min)
        self.ui.file_index_slider.setValue(_value)
        self.update_labels()

        # splitter
        self.ui.splitter.setSizes([800, 100])

        # update size of table columns
        nbr_columns = self.ui.tableWidget.columnCount()
        for _col in range(nbr_columns):
            self.ui.tableWidget.setColumnWidth(_col, self.table_column_width[_col])

        self.ui.file_index_slider.blockSignals(False)

    def update_infos_tab(self):

        if self.ui.sort_files_by_name_radioButton.isChecked():
            is_by_name = True
        else:
            is_by_name = False

        dict_data = self.dict_data

        _time_column_label = 'Time Stamp (Unix format)'
        if is_by_name:
            _time_column_label = 'Delta Time (s)'

        item = self.ui.tableWidget.horizontalHeaderItem(1)
        item.setText(_time_column_label)

        list_files = dict_data['list_images']
        list_time_stamp = dict_data['list_time_stamp']
        list_time_stamp_user = dict_data['list_time_stamp_user_format']

        if self.ui.ignore_first_image_checkbox.isChecked():
            list_files = list_files[1:]
            list_time_stamp = list_time_stamp[1:]
            list_time_stamp_user = list_time_stamp_user[1:]

        self.__clear_infos_table()

        for _row, _file_name in enumerate(list_files):
            _short_name = os.path.basename(_file_name)
            _time_stamp_unix = list_time_stamp[_row]
            if is_by_name: #cleanup format
                _time_stamp_unix = "{:.2f}".format(_time_stamp_unix)
            _time_stamp_user = list_time_stamp_user[_row]

            self.__insert_information_in_table(row=_row,
                                               col0=_short_name,
                                               col1=_time_stamp_unix,
                                               col2=_time_stamp_user)

    def __clear_infos_table(self):
        nbr_row = self.ui.tableWidget.rowCount()
        for _row in np.arange(nbr_row):
            self.ui.tableWidget.removeRow(0)

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
        self.update_profile_plot_water_intake_peak()

    def update_plots(self):
        self.update_profile_plot()
        self.update_water_intake_plot()
        self.update_profile_plot_water_intake_peak()

    def update_profile_plot(self):
        index_selected = self.ui.file_index_slider.value()
        o_profile_handler = ProfileHandler(parent=self)
        o_profile_handler.calculate_profile(index=index_selected)
        o_profile_handler.plot()

    def calculate_all_profiles(self):
        o_profile_handler = ProfileHandler(parent=self)
        o_profile_handler.calculate_profile(all=True)

    def get_profile_algo(self):
        if self.ui.add_radioButton.isChecked():
            return 'add'
        elif self.ui.mean_radioButton.isChecked():
            return 'mean'
        elif self.ui.median_radioButton.isChecked():
            return 'median'
        return ''

    def get_algorithm_selected(self):
        if self.ui.sliding_average_checkBox.isChecked():
            return 'sliding_average'
        elif self.ui.error_function_checkBox.isChecked():
            return 'error_function'
        elif self.ui.change_point_checkBox.isChecked():
            return "change_point"
        else:
            raise ValueError("algorithm not implemented yet!")

    def update_water_intake_plot(self):
        # hourglass cursor
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        algorithm_selected = self.get_algorithm_selected()

        self.calculate_all_profiles()

        o_water_intake_handler = WaterIntakeHandler(dict_profiles=self.dict_profiles,
                                                    ignore_first_image=self.ui.ignore_first_image_checkbox.isChecked(),
                                                    algorithm_selected=algorithm_selected)

        pixel_size = self.ui.pixel_size_spinBox.value()
        if algorithm_selected == 'sliding_average':
            peak = o_water_intake_handler.water_intake_peak_sliding_average
            self.water_intake_peaks_sliding_average = peak.copy()
            delta_time = o_water_intake_handler.water_intake_deltatime

        elif algorithm_selected == 'error_function':
            peak = o_water_intake_handler.water_intake_peaks_erf
            self.water_intake_peaks_erf = peak.copy()
            self.dict_error_function_parameters = o_water_intake_handler.dict_error_function_parameters
            delta_time = o_water_intake_handler.water_intake_deltatime
            self.is_data_from_max_to_min = o_water_intake_handler.is_data_from_max_to_min

            # due to the fact that the pixel reported may be from the right
            if self.is_inte_along_x_axis:
                if not self.is_data_from_max_to_min:
                    peak = [int(self.roi['height'] - _peak) for _peak in peak]
            else:
                if not self.is_data_from_max_to_min:
                    peak = [int(self.roi['width'] - peak) for peak in peak]

        elif algorithm_selected == 'change_point':
            peak = o_water_intake_handler.water_intake_peaks_change_point
            self.water_intake_peaks_change_point = peak.copy()
            delta_time = o_water_intake_handler.water_intake_deltatime

        else:
            raise NotImplementedError("Algorithm not implemented yet!")

        # we want absolute pixel value
        if self.is_inte_along_x_axis:
            peak = [_peak + int(self.roi['y0']) for _peak in peak]
        else:
            peak = [_peak + int(self.roi['x0']) for _peak in peak]

        if self.ui.pixel_radioButton.isChecked():  # pixel
            y_label = 'Pixel Position'
        else:  # distance
            peak = [float(_peak) * pixel_size for _peak in peak]
            y_label = 'Distance (mm)'

        self.dict_water_intake = {}
        self.dict_water_intake['xaxis'] = delta_time
        self.dict_water_intake['yaxis'] = peak

        self.water_intake.clear()
        if algorithm_selected == 'error_function':
            error = o_water_intake_handler.dict_error_function_parameters_error
            top = error
            bottom = error
            peak = np.array(peak)
            self.dict_water_intake['error'] = error

            # cleaning the error to make sure their values is not bigger than the peak value
            for _index, _err in enumerate(error):
                if _err > peak[_index]:
                    error[_index] = np.sqrt(peak[_index])

            err = pg.ErrorBarItem(x=delta_time,
                                  y=peak,
                                  top=top,
                                  bottom=bottom)

            self.water_intake.addItem(err)
            self.water_intake.plot(delta_time, peak, symbolPen=None,
                                   pen=None,
                                   symbol='o',
                                   symbolBruch=(200,200,200,50))
        else:
            self.water_intake.plot(delta_time, peak, symbolPen=None,
                                   pen=None,
                                   symbol='o',
                                   symbolBruch=(200,200,200,50))

        self.water_intake.setLabel('left', y_label)
        self.water_intake.setLabel('bottom', 'Delta Time')

        QApplication.restoreOverrideCursor()

    def update_profile_plot_water_intake_peak(self):
        # display value of current water intake peak in profile plot
        index_selected = self.ui.file_index_slider.value()
        if self.ui.ignore_first_image_checkbox.isChecked():
            index_selected -= 2
        else:
            index_selected -= 1

        algorithm_selected = self.get_algorithm_selected()
        if algorithm_selected == 'sliding_average':
            _water_intake_peaks = self.water_intake_peaks_sliding_average.copy()
            if self.is_inte_along_x_axis:
                _offset = int(self.roi['y0'])
            else:
                _offset = int(self.roi['x0'])
            peak_value = _water_intake_peaks[index_selected] +_offset
        elif algorithm_selected == 'error_function':
            _water_intake_peaks = self.water_intake_peaks_erf.copy()
            is_data_from_max_to_min = self.is_data_from_max_to_min
            if self.is_inte_along_x_axis:
                if is_data_from_max_to_min:
                    peak_value = _water_intake_peaks[index_selected] + int(self.roi['y0'])
                else:
                    peak_value = int(self.roi['height'] + self.roi['y0'] - _water_intake_peaks[index_selected])
            else:
                if is_data_from_max_to_min:
                    peak_value = _water_intake_peaks[index_selected] + int(self.roi['x0'])
                else:
                    peak_value = int(self.roi['width'] + self.roi['x0'] - _water_intake_peaks[index_selected])
        elif algorithm_selected == 'change_point':
            _water_intake_peaks = self.water_intake_peaks_change_point.copy()
            if self.is_inte_along_x_axis:
                _offset = int(self.roi['y0'])
            else:
                _offset = int(self.roi['x0'])
            peak_value = _water_intake_peaks[index_selected] +_offset
        else:
            raise NotImplemented

        self.profile_vline = pg.InfiniteLine(angle=90, movable=False,
                                             pos=peak_value)
        self.profile.addItem(self.profile_vline, ignoreBounds=True)

        # display fitting function for error function
        if self.get_algorithm_selected() == 'error_function':

            index_selected = self.ui.file_index_slider.value()-1
            dict_error_function_parameters = self.dict_error_function_parameters.copy()
            # pprint.pprint(dict_error_function_parameters)
            _fit_parameters = dict_error_function_parameters[str(index_selected)]

            xdata = self.live_x_axis
            fitting_xdata = np.arange(len(xdata))
            ydata = WaterIntakeHandler.fitting_function(fitting_xdata,
                                                        _fit_parameters['c'],
                                                        _fit_parameters['w'],
                                                        _fit_parameters['m'],
                                                        _fit_parameters['n'])

            if not is_data_from_max_to_min:
                ydata = ydata[::-1]

            self.profile.plot(xdata, ydata, pen=(255,0,0))



    def export_profile_clicked(self):
        o_profile_handler = ProfileHandler(parent=self)
        o_profile_handler.calculate_profile(all=True)
        o_profile_handler.export()

    def get_profile(self, image):
        """return the 1D profile of the image using the correct integration method (add, mean, median)"""

        if self.is_inte_along_x_axis:
            _axis_to_integrate = 1
        else:
            _axis_to_integrate = 0
        _algo_used = self.get_profile_algo()

        if _algo_used == 'add':
            _profile = np.sum(image, axis=_axis_to_integrate)
        elif _algo_used == 'mean':
            _profile = np.mean(image, axis=_axis_to_integrate)
        elif _algo_used == 'median':
            _profile = np.median(image, axis=_axis_to_integrate)
        else:
            raise NotImplementedError
        return _profile

    def export_water_intake_clicked(self):
        _export_folder = QFileDialog.getExistingDirectory(self,
                                                          directory=self.working_dir,
                                                          caption = 'Select Output Folder',
                                                          options = QFileDialog.ShowDirsOnly)
        if _export_folder:
            export_folder = os.path.abspath(_export_folder)

            dict_water_intake = self.dict_water_intake
            if dict_water_intake == {}:
                return

            x_axis = dict_water_intake['xaxis']
            y_axis = dict_water_intake['yaxis']

            nbr_files = len(x_axis)

            # metadata
            _algo_used = self.get_profile_algo()
            _master_algo_used = self.get_algorithm_selected()
            _roi = self.roi
            x0 = _roi['x0']
            y0 = _roi['y0']
            width = _roi['width']
            height = _roi['height']

            if _master_algo_used == 'error_function':
                error = dict_water_intake['error']

            list_images = self.dict_data['list_images']
            full_input_folder = os.path.dirname(list_images[0])
            short_input_folder = os.path.basename(full_input_folder)

            yaxis_label = self.__get_water_intake_yaxis_label()
            if yaxis_label == 'distance':
                yaxis_label += "(mm)"

            if self.is_inte_along_x_axis:
                inte_direction = 'x_axis'
            else:
                inte_direction = 'y_axis'

            metadata = []
            metadata.append("# Water Intake Signal ")
            metadata.append("# roi [x0, y0, width, height]: [{}, {}, {}, {}]".format(x0, y0, width, height))
            metadata.append("# integration direction: {}".format(inte_direction))
            metadata.append("# input folder: {}".format(full_input_folder))
            metadata.append("# algorithm used: {}".format(_algo_used))
            metadata.append("# calculation used: {}".format(_master_algo_used))
            metadata.append("# ")
            metadata.append("# Time(s), {}, error".format(yaxis_label))

            export_file_name = "water_intake_of_{}_with_{}input_files.txt".format(short_input_folder, nbr_files)
            full_export_file_name = os.path.join(export_folder, export_file_name)

            if _master_algo_used == 'error_function':
                metadata.append("# Time(s), {}, error".format(yaxis_label))
                data = [ "{}, {}, {}".format(_x_axis, _y_axis, _error) for _x_axis, _y_axis, _error in zip(x_axis, y_axis, error)]
            else:
                metadata.append("# Time(s), {}".format(yaxis_label))
                data = [ "{}, {}".format(_x_axis, _y_axis) for _x_axis, _y_axis, _error in zip(x_axis, y_axis)]

            display(HTML("Exported water intake file: {}".format(full_export_file_name)))
            make_ascii_file(metadata=metadata, data=data, output_file_name=full_export_file_name, dim='1d')

    def __get_water_intake_yaxis_label(self):
        if self.ui.pixel_radioButton.isChecked():
            return 'pixel'
        else:
            return 'distance'

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
        return image
        # range_max = 1.2
        # _result_range = np.where(image > range_max)
        # image[_result_range] = np.NaN
        # return image

    def update_image(self):

        _view = self.ui.image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()

        first_update = False
        if self.histogram_level == []:
            first_update = True
        _histo_widget = self.ui.image_view.getHistogramWidget()
        self.histogram_level = _histo_widget.getLevels()

        index_selected = self.ui.file_index_slider.value()
        _image = self.dict_data['list_data'][index_selected-1]
        _image = np.transpose(_image)
        _image = self._clean_image(_image)
        _image = self._force_range(_image)
        self.current_image = _image
        self.ui.image_view.setImage(_image)
        _view_box.setState(_state)

        if not first_update:
            _histo_widget.setLevels(self.histogram_level[0], self.histogram_level[1])

    def slider_changed(self, value):
        self.ui.file_index_value.setText(str(value))
        self.update_image()
        self.update_profile_plot()
        self.update_profile_plot_water_intake_peak()

    def _water_intake_yaxis_checkbox_changed(self):
        _status = self.ui.distance_radioButton.isChecked()
        self.ui.water_intake_distance_label.setEnabled(_status)
        self.ui.pixel_size_spinBox.setEnabled(_status)
        self.ui.pixel_size_units.setEnabled(_status)
        self.update_water_intake_plot()

    def _pixel_size_spinBox_changed(self):
        self.update_water_intake_plot()

    # files sorting
    def sorting_files_checkbox_clicked(self):
        # hourglass
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        is_sorting_by_name = self.ui.sort_files_by_name_radioButton.isChecked()
        self.ui.time_between_runs_label.setEnabled(is_sorting_by_name)
        self.ui.time_between_runs_spinBox.setEnabled(is_sorting_by_name)
        self.ui.time_between_runs_units_label.setEnabled(is_sorting_by_name)
        self.__sort_files()
        self.update_infos_tab()
        self.update_image()
        # self.update_plots()
        self.update_profile_plot()
        QApplication.restoreOverrideCursor()

    def __sort_files(self):
        # reformat name to make sure the last digit have 4 digits
        is_by_name = self.ui.sort_files_by_name_radioButton.isChecked()

        if is_by_name:
            try:
                self._fix_index_of_files()
            except ValueError:
                pass
        else:
            self._reset_dict()

        dict_data = self.dict_data
        list_images = np.array(dict_data['list_images'].copy())
        list_time_stamp = np.array(dict_data['list_time_stamp'].copy())
        list_time_stamp_user_format = np.array(dict_data['list_time_stamp_user_format'].copy())
        list_data = np.array(dict_data['list_data'].copy())

        if is_by_name:
            sort_index = np.argsort(list_images)
        else:
            sort_index = np.argsort(list_time_stamp)

        sorted_list_images = list_images[sort_index]
        sorted_list_time_stamp = list_time_stamp[sort_index]
        sorted_list_time_stamp_user_format = list_time_stamp_user_format[sort_index]
        sorted_list_data = list_data[sort_index]

        dict_data['list_images'] = list(sorted_list_images)
        dict_data['list_time_stamp'] = list(sorted_list_time_stamp)
        dict_data['list_time_stamp_user_format'] = list(sorted_list_time_stamp_user_format)
        dict_data['list_data'] = sorted_list_data

        self.dict_data = dict_data

        if is_by_name:
            # define list of time stamp using manual delta time defined
            delta_time = self.ui.time_between_runs_spinBox.value()
            nbr_files = len(list_images)
            new_time_stamp = np.arange(nbr_files) * delta_time
            self.dict_data['list_time_stamp'] = new_time_stamp

    def _reset_dict(self):
        self.dict_data = self.dict_data_raw.copy()

    def _fix_index_of_files(self):
        """reformat file name to make sure index has 4 digits
        """
        _dict_data_raw = self.dict_data_raw
        list_files = _dict_data_raw['list_images'].copy()
        formated_list_files = []

        re_string = r"^(?P<part1>\w*)_(?P<index>\d+)$"
        for _file in list_files:
            dirname = os.path.dirname(_file)
            basename = os.path.basename(_file)
            [base, ext] = os.path.splitext(basename)
            base = base.replace(" ","") # remove white spaces in name of file
            m = re.match(re_string, base)
            if m is None:
                raise ValueError
            else:
                part1 = m.group('part1')
                index = int(m.group('index'))
                new_index = "{:04d}".format(index)
                new_file = os.path.join(dirname, part1 + '_' + new_index + ext)
                formated_list_files.append(new_file)

        self.dict_data = self.dict_data_raw.copy()
        self.dict_data['list_images'] = formated_list_files

    def time_between_runs_spinBox_changed(self):
        self.sorting_files_checkbox_clicked()

    def profile_algo_changed(self):
        self.update_profile_plot()

    def export_table_button_clicked(self):
        _export_folder = QFileDialog.getExistingDirectory(self,
                                                          directory=self.working_dir,
                                                          caption = 'Select Output Folder',
                                                          options = QFileDialog.ShowDirsOnly)

        if _export_folder:
            export_folder = os.path.abspath(_export_folder)

            dict_data = self.dict_data
            list_images = dict_data['list_images']
            input_folder = os.path.basename(os.path.dirname(list_images[0]))

            output_file_name = os.path.join(export_folder, input_folder + '_sorting_table.txt')

            list_time = dict_data['list_time_stamp']
            list_time_stamp_user_format = dict_data['list_time_stamp_user_format']

            is_sorting_by_name = self.ui.sort_files_by_name_radioButton.isChecked()
            if is_sorting_by_name:
                _time_label = 'Time Stamp (unix)'
            else:
                _time_label = 'Delta Time (s)'

            metadata = ["#File Name, {}, Time Stamp (user format)".format(_time_label)]
            data = ["{}. {}, {}".format(_file, _time, _timer_user) for (_file, _time, _timer_user) in
                    zip(list_images, list_time, list_time_stamp_user_format)]

            make_ascii_file(metadata=metadata, data=data, output_file_name=output_file_name, dim='1d')
            display(HTML("Table has been exported in {}".format(output_file_name)))

    def import_dsc_clicked(self):
        _dsc_folder = QFileDialog.getExistingDirectory(self,
                                                       directory=self.working_dir,
                                                       caption = 'Select Output Folder',
                                                       options = QFileDialog.ShowDirsOnly)
        if _dsc_folder:
            dsc_folder = os.path.abspath(_dsc_folder)

            list_dsc_files = glob.glob(os.path.join(dsc_folder, "*.dsc"))
            o_dsc_reader = DscReader(list_files = list_dsc_files)
            o_dsc_reader.read()
            o_dsc_reader.build_coresponding_file_image_name()
            o_dsc_reader.make_tif_file_name_the_key()
            self.dict_time_stamp_vs_tiff = o_dsc_reader.dict_time_stamp_vs_tiff
            self.match_dsc_timestamp_with_original_dict_data()
            self.sorting_files_checkbox_clicked()
            self.update_infos_tab()
            self.update_plots()

    def match_dsc_timestamp_with_original_dict_data(self):
        dict_disc = self.dict_time_stamp_vs_tiff
        dict_data_raw = self.dict_data_raw

        list_images = dict_data_raw['list_images']

        new_list_time_stamp = []
        new_list_time_stamp_user_format = []

        for _key in list_images:
            _short_key = os.path.basename(_key)
            new_list_time_stamp.append(dict_disc[_short_key]['time_stamp'])
            new_list_time_stamp_user_format.append(dict_disc[_short_key]['time_stamp_user_format'])

        self.dict_data_raw['list_time_stamp'] = new_list_time_stamp.copy()
        self.dict_data_raw['list_time_stamp_user_format'] = new_list_time_stamp_user_format.copy()

    def algorithm_changed(self):
        self.update_plots()

    def integration_direction_changed(self):
        self.is_inte_along_x_axis = self.ui.x_axis_integration_radioButton.isChecked()
        self.update_plots()

    def ignore_first_image_checkbox_clicked(self):
        ignore_first_image = self.ui.ignore_first_image_checkbox.isChecked()
        self._init_widgets(ignore_first_image=ignore_first_image, first_init=False)
        self.update_infos_tab()
        self.update_image()
        self.update_plots()

    def help_button_clicked(self):
        import webbrowser
        webbrowser.open("https://neutronimaging.pages.ornl.gov/en/tutorial/notebooks/water_intake_profile_calculator/")

    def ok_button_clicked(self):
        # do soemthing here
        self.close()

    def rebin_slider_changed(self, new_value):
        self.update_plots()

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

        self.files_ui = fileselector.FileSelectorPanel(instruction='Select Images ...',
                                                       start_dir=self.working_dir,
                                                       next=self.load_and_plot,
                                                       multiple=True)

        self.files_ui.show()

    def load_and_plot(self, list_images):
        self.load(list_images)
        #self.launch_plot()

    def launch_plot(self):
        o_gui = WaterIntakeProfileSelector(dict_data=self.dict_files)
        o_gui.show()

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

        list_images = dict_time_stamp['list_images'].copy()
        list_time_stamp = dict_time_stamp['list_time_stamp'].copy()
        list_time_stamp_user_format = dict_time_stamp['list_time_stamp_user_format'].copy()

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

class ProfileHandler(object):

    _profile = []
    _bins = []
    x0 = 0
    y0 = 0
    x1 = 0
    y1 = 0

    def __init__(self, parent=None):
        self.parent = parent
        
    def calculate_profile(self, all=False, index=0):
        dict_data = self.parent.dict_data
        self._save_roi_corners()

        if all: # all profiles
            if self.parent.ui.ignore_first_image_checkbox.isChecked():
                first_image = 1
            else:
                first_image = 0

            nbr_images = len(dict_data['list_images'])
            for index in np.arange(first_image, nbr_images):
                self.__calculate_individual_profile(index_file=index, save=True)

        else: # only index
            self.__calculate_individual_profile(index_file=index-1)

    def __calculate_individual_profile(self, index_file=0, save=False):
        _image = self.parent.dict_data['list_data'][index_file]
        _image_of_roi = _image[self.y0:self.y1, self.x0:self.x1]
        _profile = self.get_profile(_image_of_roi)

        # rebin profile
        bin_size = self.parent.ui.rebin_spinBox.value()

        # calculate bin array
        bins = []
        index = 0
        while (index < len(_profile)):
            if np.mod(index, bin_size) != 0:
                pass
            else: # end of bin
                bins.append(index)

            index += 1

        bins = np.array(bins)

        # make sure the size of profile agrees with the bin size defined
        if not (np.mod(len(_profile), bin_size) == 0):
            _profile = _profile[:-np.mod(len(_profile), bin_size)]
        _profile = np.reshape(_profile, (int(len(_profile)/bin_size), bin_size))
        _profile = np.mean(_profile, axis=1)

        self._profile = _profile
        self._bins = bins

        if save:
            list_time_stamp = self.parent.dict_data['list_time_stamp']
            is_sorting_by_name = self.parent.ui.sort_files_by_name_radioButton.isChecked()
            if is_sorting_by_name:
                time_stamp_first_file = 0
            else:
                time_stamp_first_file = float(list_time_stamp[0])

            time_stamp = float(list_time_stamp[index_file])
            delta_time = time_stamp - time_stamp_first_file

            if self.parent.is_inte_along_x_axis:
                x_axis = self._bins + int(self.y0)
            else:
                x_axis = self._bins + int(self.x0)

            x_axis = x_axis[:len(self._profile)]

            self.parent.dict_profiles[str(index_file)] = {'data': _profile,
                                                          'x_axis': x_axis,
                                                          'delta_time': delta_time}

    def plot(self):
        self.parent.profile.clear()
        if self.parent.is_inte_along_x_axis:
            y_axis_label = 'Y pixels'
            x_axis = self._bins + int(self.y0)
        else:
            y_axis_label = 'X pixels'
            x_axis = self._bins + int(self.x0)

        x_axis = x_axis[:len(self._profile)]

        self.parent.live_x_axis = x_axis
        self.parent.profile.plot(x_axis, self._profile)
        self.parent.profile.setLabel('left', 'Counts')
        self.parent.profile.setLabel('bottom', y_axis_label)

    def get_profile(self, image):
        """return the 1D profile of the image using the correct integration method (add, mean, median)"""

        if self.parent.is_inte_along_x_axis:
            _axis_to_integrate = 1
        else:
            _axis_to_integrate = 0
        _algo_used = self.parent.get_profile_algo()

        if _algo_used == 'add':
            _profile = np.sum(image, axis=_axis_to_integrate)
        elif _algo_used == 'mean':
            _profile = np.mean(image, axis=_axis_to_integrate)
        elif _algo_used == 'median':
            _profile = np.median(image, axis=_axis_to_integrate)
        else:
            raise NotImplementedError
        return _profile

    def _save_roi_corners(self):
        _roi = self.parent.roi
        self.x0 = _roi['x0']
        self.y0 = _roi['y0']
        width = _roi['width']
        height = _roi['height']
        self.x1 = self.x0 + width
        self.y1 = self.y0 + height

    def export(self):
        # select output folder
        _export_folder = QFileDialog.getExistingDirectory(self.parent,
                                                          directory=self.parent.working_dir,
                                                          caption="Select Output Folder",
                                                          options=QFileDialog.ShowDirsOnly)
        if _export_folder:
            export_folder = os.path.abspath(_export_folder)

            dict_data = self.parent.dict_data
            list_images = dict_data['list_images']
            list_time_stamp = dict_data['list_time_stamp']
            #list_data = dict_data['list_data']
            list_time_stamp_user_format = dict_data['list_time_stamp_user_format']
            _algo_used = self.parent.get_profile_algo()

            # get metadata roi selection
            _roi = self.parent.roi
            x0 = _roi['x0']
            y0 = _roi['y0']
            width = _roi['width']
            height = _roi['height']
            # x1 = x0 + width
            # y1 = y0 + height

            input_folder = os.path.dirname(list_images[0])

            nbr_images = len(list_images)
            self.parent.eventProgress.setMinimum(1)
            self.parent.eventProgress.setMaximum(nbr_images)
            self.parent.eventProgress.setValue(1)
            self.parent.eventProgress.setVisible(True)

            if self.parent.is_inte_along_x_axis:
                inte_direction = 'x_axis'
            else:
                inte_direction = 'y_axis'

            if self.parent.ui.ignore_first_image_checkbox.isChecked():
                first_image = 1
            else:
                first_image = 0

            for index in np.arange(first_image, nbr_images):
                _short_file_name = os.path.basename(list_images[index])
                [_basename, _] = os.path.splitext(_short_file_name)
                output_file_name = os.path.join(export_folder, _basename + '_profile.txt')

                metadata = []
                metadata.append("# Profile over ROI selected integrated along x-axis")
                metadata.append("# roi [x0, y0, width, height]: [{}, {}, {}, {}]".format(x0, y0, width, height))
                metadata.append("# integration direction: {}".format(inte_direction))
                metadata.append("# folder: {}".format(input_folder))
                metadata.append("# filename: {}".format(_short_file_name))
                metadata.append("# timestamp (unix): {}".format(list_time_stamp[index]))
                metadata.append("# timestamp (user format): {}".format(list_time_stamp_user_format[index]))
                metadata.append("# algorithm used: {}".format(_algo_used))
                metadata.append("# ")
                metadata.append("# pixel, counts")

                _profile = self.parent.dict_profiles[str(index)]['data']
                _pixel_index = self.parent.dict_profiles[str(index)]['x_axis']
                pixel_profile = zip(_pixel_index, _profile)

                data = []
                for _pixel_index, _counts in pixel_profile:
                    _line = "{}, {}".format(_pixel_index + y0, _counts)
                    data.append(_line)

                make_ascii_file(metadata=metadata,
                                data=data,
                                output_file_name=output_file_name,
                                dim='1d')

                self.parent.eventProgress.setValue(index)

            self.parent.eventProgress.setVisible(False)
            display(HTML("Exported Profiles files ({} files) in {}".format(nbr_images, export_folder)))
