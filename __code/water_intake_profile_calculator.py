import ipywe.fileselector

from IPython.core.display import HTML
from IPython.core.display import display
from ipywidgets import widgets
from ipywidgets.widgets import interact

import matplotlib.pyplot as plt
import numpy as np
import os
import re
import pandas as pd

import matplotlib.gridspec as gridspec
import pytz
import datetime

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

from __code.metadata_handler import MetadataHandler
from __code.file_handler import retrieve_time_stamp
from __code import file_handler

from __code.ui_water_intake_profile  import Ui_MainWindow as UiMainWindow

class WaterIntakeProfileSelector(QMainWindow):

    list_data = []
    dict_data = {}
    current_image = []
    ignore_first_image_checked = True
    roi_width = 0.01
    roi = {'x0': 0, 'y0': 0, 'width': 200, 'height': 200}
    table_column_width = [350, 150, 200]

    def __init__(self, parent=None, dict_data={}):

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
            (maybe hidden behind this browser!)</span>'))

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Profile Selector")

        self.dict_data = dict_data
        self.list_data = dict_data['list_data'][1:]
        self._init_pyqtgraph()
        self._init_widgets()
        self.update_image()
        self.update_plots()
        self.update_infos_tab()

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
        self.ui.x0.setText(str(_x0))
        self.ui.y0.setText(str(_y0))
        self.ui.width.setText(str(_width))
        self.ui.height.setText(str(_height))

    def refresh_water_intake_plot_clicked(self):
        pass

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

    def get_profile_algo(self):
        if self.ui.add_radioButton.isChecked():
            return 'add'
        elif self.ui.mean_radioButton.isChecked():
            return 'mean'
        elif self.ui.median_radioButton.isChecked():
            return 'median'
        return ''

    def update_water_intake_plot(self):
        pass

    def export_profile_clicked(self):


    def export_water_intake_clicked(self):
        pass

    def display_imported_files_clicked(self):
        print("displaying imported files")

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
                                                             multiple=True)

        self.files_ui.show()

    def sort_and_load(self):
        list_images = self.files_ui.selected
        dict_time_stamp = retrieve_time_stamp(list_images)
        self.__sort_files_using_time_stamp(dict_time_stamp)
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












