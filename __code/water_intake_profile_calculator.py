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
    current_image = []
    ignore_first_image_checked = True
    roi_width = 0.01
    roi = {'x0': 0, 'y0': 0, 'width': 200, 'height': 200}

    def __init__(self, parent=None, dict_data={}):

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
            (maybe hidden behind this browser!)</span>'))

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Profile Selector")

        self.list_data = dict_data['list_data'][1:]
        self._init_pyqtgraph()
        self._init_widgets()
        self.update_image()
        self.update_plots()

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
        pass

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

    def update_image(self):
        index_selected = self.ui.file_index_slider.value()
        _image = self.list_data[index_selected-1]
        self.current_image = _image
        self.ui.image_view.setImage(_image)

    def slider_changed(self, value):
        self.ui.file_index_value.setText(str(value))
        self.update_image()
        self.update_profile_plot()

    def profile_algo_changed(self):
        print("profile algo changed")
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
        o_load.load(file=self.dict_time_stamp['list_images'], notebook=True)
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

        self.dict_time_stamp = {'list_images': list(sorted_list_images),
                                'list_time_stamp': sorted_list_time_stamp,
                                'list_time_stamp_user_format': sorted_list_time_stamp_user_format}















    ### OLD FILE

    def select_counts_vs_time_files(self):
        self.list_files_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select Counts vs Time Files ...',
                                                              start_dir=self.working_dir,
                                                              multiple=True)

        self.list_files_ui.show()

    def retrieve_metadata(self, file_name):
        """
        return a dictionary of the metadata (plus number of comment lines)
        """
        with open(file_name) as f:
            _metadata = {}
            _nbr_comment_line = 0
            for line in f:
                li = line.strip()
                if li.startswith("#"):
                    _nbr_comment_line += 1
                    m = re.match(r"^#(?P<tag_name>[,\(\)\s\w]*):(?P<tag_value>.*)", li)
                    if m is None:
                        continue
                    _metadata[m.group('tag_name')] = m.group('tag_value').strip()
            _metadata['nbr_comment_line'] = _nbr_comment_line
            return _metadata

    def retrieve_data(self, file_name, nbr_comment_line=0, col_names=None):
        file_0 = pd.read_csv(file_name,
                             skiprows=nbr_comment_line,
                             header=None,
                             names=col_names)
        return file_0

    def format_col_names(self, col_names):
        _col_names = [_col.strip() for _col in col_names]
        return _col_names

    def retrieve_data_and_metadata(self):

        self.list_files = self.list_files_ui.selected

        w = widgets.IntProgress()
        w.max = len(self.list_files)
        display(w)
        index = 0

        files_data = {}
        files_metadata = {}
        for index, file in enumerate(self.list_files):
            _metadata = self.retrieve_metadata(file)
            files_metadata[file] = _metadata
            _col_names = _metadata['Label'].split(',')
            _new_col_names = self.format_col_names(_col_names)
            _data = self.retrieve_data(file,
                                      nbr_comment_line=_metadata['nbr_comment_line'],
                                      col_names=_new_col_names)
            files_data[file] = _data

            index += 1
            w.value = index

        self.files_data = files_data
        self.files_metadata = files_metadata

        w.close()

    def calculate_water_intake_peak(self):

        pixel_index = self.files_data[self.list_files[0]]
        nbr_pixel = len(pixel_index)

        water_intake_peak = []
        time_stamps = []
        for _index, _file in enumerate(self.list_files):
            counts = self.files_data[_file]['counts'].values
            delta_array = []
            for _pixel in range(0, nbr_pixel - 1):
                _o_range = MeanRangeCalculation(data=counts)
                _o_range.calculate_left_right_mean(pixel=_pixel)
                _o_range.calculate_delta_mean_square()
                delta_array.append(_o_range.delta_square)

            time_stamps.append(self.files_metadata[_file]['Delta Time (s)'])

            _peak_value = delta_array.index(max(delta_array[0:nbr_pixel - 5]))
            water_intake_peak.append(_peak_value)

        self.water_intake_peak = water_intake_peak
        self.time_stamps = time_stamps

    def display_water_intake_vs_profile(self):

        self.retrieve_data_and_metadata()
        self.calculate_water_intake_peak()

        water_intake_peak = self.water_intake_peak
        list_files = self.list_files
        metadata = self.files_metadata

        def display_intake_vs_profile(file_index):

            plt.figure(figsize=(5,5))
            ax_img = plt.subplot(111)
            _file = list_files[file_index]
            _data = self.files_data[_file]['counts'].values
            _peak = float(water_intake_peak[file_index])
            _metadata = metadata[_file]
            _rebin = float(_metadata['Rebin in y direction'])
            _metadata_entry = _metadata['ROI selected (y0, x0, height, width)']
            m = re.match(r"\((?P<y0>\d*), (?P<x0>\d*), (?P<height>\d*), (?P<width>\d*)\)",
                         _metadata_entry)
            y0 = float(m.group('y0'))
            height = float(m.group('height'))

            _real_peak = (_peak + y0) * _rebin
            _real_axis = np.arange(y0, height, _rebin)

            ax_img.plot(_real_axis, _data, '.')
            plt.title(os.path.basename(_file))
            ax_img.axvline(x=_real_peak, color='r')

        _ = interact(display_intake_vs_profile,
                     file_index = widgets.IntSlider(min=0,
                                                    max=len(list_files)-1,
                                                    value=0,
                                                    description='File Index'))

    def display_water_intake_peak_in_px(self):


        fig = plt.figure(figsize=(5, 5))
        plt.plot(self.time_stamps, self.water_intake_peak)
        plt.xlabel("Delta Time (s)")
        plt.ylabel("Peak Position (pixel)")
        plt.title("Peak vs Delta Time (s)")

    def define_pixel_size(self):

        box = widgets.HBox([widgets.Label("Size/Pixel Ratio"),
                            widgets.FloatText(value=1,
                                              step=0.1,
                                              layout=widgets.Layout(width='10%')),
                            widgets.Label("mm/px")])

        display(box)
        self.ratio_widget = box.children[1]

    def display_water_intake_peak_in_mm(self):

        water_intake_peak_px = np.array(self.water_intake_peak)
        self.water_intake_peak_mm = water_intake_peak_px * self.ratio_widget.value

        fig = plt.figure(figsize=(5, 5))
        plt.plot(self.time_stamps, self.water_intake_peak_mm)
        plt.xlabel("Delta Time (s)")
        plt.ylabel("Peak Position (mm)")
        plt.title("Peak vs Delta Time (s)")

    def select_output_folder(self):
        self.output_folder_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select Output Folder ...',
                                                                     start_dir=self.working_dir,
                                                                     type='directory')
        self.output_folder_ui.show()

    def export(self):

        output_folder = os.path.abspath(self.output_folder_ui.selected)
        short_file_name = os.path.basename(os.path.abspath(os.path.dirname(self.list_files[0]))) + '.txt'
        output_file_name = os.path.join(output_folder, short_file_name)

        ascii_text = "# Source data: {}\n".format(os.path.basename(os.path.dirname(self.list_files[0])))
        ascii_text += '# time_stamp(s), water_intake_position (mm)\n'
        for _index in range(len(self.time_stamps)):
            _x_value = self.time_stamps[_index]
            _y_value = self.water_intake_peak_mm[_index]
            ascii_text += "{}, {}\n".format(_x_value, _y_value)

        make_ascii_file_from_string(text=ascii_text, filename=output_file_name)

        display(HTML('<span style="font-size: 20px; color:blue">File created: ' +
                     os.path.basename(output_file_name) + '<br> ' +
                     'In folder: ' + os.path.dirname(output_file_name) + '</span>'))


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