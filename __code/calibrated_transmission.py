from IPython.core.display import HTML
from IPython.core.display import display

import numpy as np
import os
import copy
import pyqtgraph as pg

try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui, QtWidgets
    from PyQt4.QtGui import QMainWindow, QDialog
except ImportError:
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5 import QtCore, QtGui, QtWidgets
    from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

from __code.color import  Color
from __code.file_handler import retrieve_time_stamp, make_ascii_file
from __code.ui_calibrated_transmission import Ui_MainWindow as UiMainWindow


class CalibratedTransmissionUi(QMainWindow):

    data_dict = {}
    timestamp_dict = {}

    histogram_level = []
    col_width = 65
    table_column_width = [col_width, col_width, col_width, col_width, 100]
    summary_table_width = [300, 150, 100]
    default_measurement_roi = {'x0': 0, 'y0': 0,
                               'width': np.NaN, 'height': np.NaN}

    # where the mean counts and calibrated value will be displayed
    calibration = {}      # '1' : {'mean_counts' : _mean, 'value': _value}

    measurement_dict = {}   # '1': [ measurement data calibrated ]

    calibration_widgets = {}
    calibration_widgets_label = {}
    calibrated_roi = {'1': {'x0': 0,
                            'y0': 0,
                            'width': 200,
                            'height': 200,
                            'value': 1,  #np.NaN
                            },
                      '2': {'x0': np.NaN,
                            'y0': np.NaN,
                            'width': 200,
                            'height': 200,
                            'value': 10, #np.NaN
                            },
                      }

    roi_ui_measurement = list() # keep record of all the pyqtgraph.ROI ui
    roi_ui_calibrated = []

    live_image = []

    def __init__(self, parent=None, working_dir='', data_dict=None):

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
            (maybe hidden behind this browser!)</span>'))

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Calibrated Transmission")

        self.working_dir = working_dir
        self.data_dict = data_dict # Normalization data dictionary  {'file_name': [],
                                                                     #'data': [[...],[...]]],
                                                                     #'metadata': [],
                                                                     #'shape': {}}

        # untouched array of images (used to move and rotate images)
        self.data_dict_raw = copy.deepcopy(data_dict)

        # initialization
        self.init_timestamp_dict()
        self.init_table()
        self.init_parameters()
        self.init_widgets()
        self.init_pyqtgrpah()
        self.init_statusbar()

        # display first image
        self.slider_file_changed(-1)

        self.ui.tableWidget.cellChanged['int', 'int'].connect(self.cell_changed)

    # initialization
    def init_timestamp_dict(self):
        list_files = self.data_dict['file_name']
        self.timestamp_dict = retrieve_time_stamp(list_files)

    def init_statusbar(self):
        pass
        # self.ui.info_label = QtGui.QLabel("")
        # self.ui.statusbar.addPermanentWidget(self.ui.info_label)

    def init_table(self):
        list_files_full_name = self.data_dict['file_name']
        list_files_short_name = [os.path.basename(_file) for _file in list_files_full_name]

        list_time_stamp = self.timestamp_dict['list_time_stamp']
        list_time_stamp_user_format = self.timestamp_dict['list_time_stamp_user_format']
        time_0 = list_time_stamp[0]
        for _row, _file in enumerate(list_files_short_name):
            self.ui.summary_table.insertRow(_row)
            self.set_item_summary_table(row=_row, col=0, value=_file)
            self.set_item_summary_table(row=_row, col=1, value=list_time_stamp_user_format[_row])
            _offset = list_time_stamp[_row] - time_0
            self.set_item_summary_table(row=_row, col=2, value="{:0.2f}".format(_offset))

    # def init_parameters(self):
    #     nbr_files = len(self.data_dict['file_name'])
    #     self.nbr_files = nbr_files
    #     _color = Color()
    #     self.list_rgb_profile_color = _color.get_list_rgb(nbr_color=nbr_files)
    #
    #     o_marker = MarkerDefaultSettings(image_reference=self.reference_image)
    #     self.o_MarkerDefaultSettings = o_marker

    def init_pyqtgrpah(self):
        # image
        self.ui.image_view = pg.ImageView(view=pg.PlotItem())
        self.ui.image_view.ui.menuBtn.hide()
        self.ui.image_view.ui.roiBtn.hide()
        vertical_layout = QtGui.QVBoxLayout()
        vertical_layout.addWidget(self.ui.image_view)
        self.ui.pyqtgraph_widget.setLayout(vertical_layout)

        # measurement
        self.ui.measurement_view = pg.PlotWidget()
        self.legend = self.ui.measurement_view.addLegend()
        vertical_layout2 = QtGui.QVBoxLayout()
        vertical_layout2.addWidget(self.ui.measurement_view)
        self.ui.measurement_widget.setLayout(vertical_layout2)

        def define_roi(roi_dict, callback_function):
            cal = pg.RectROI([roi_dict['x0'], roi_dict['y0']],
                             roi_dict['height'],
                             roi_dict['width'],
                             pen=roi_dict['color'])
            cal.addScaleHandle([1, 1], [0, 0])
            cal.addScaleHandle([0, 0], [1, 1])
            cal.sigRegionChanged.connect(callback_function)
            self.ui.image_view.addItem(cal)
            return cal

        # calibration
        calibration_roi = self.calibrated_roi
        roi1 = define_roi(calibration_roi['1'], self.calibration1_roi_moved)
        self.roi_ui_calibrated.append(roi1)
        roi2 = define_roi(calibration_roi['2'], self.calibration2_roi_moved)
        self.roi_ui_calibrated.append(roi2)

    def init_widgets(self):
        """size and label of any widgets"""
        self.ui.splitter.setSizes([250, 130])

        # file slider
        self.ui.file_slider.setMaximum(len(self.data_dict['data'])-1)

        # update size of table columns
        nbr_columns = self.ui.tableWidget.columnCount()
        for _col in range(nbr_columns):
            self.ui.tableWidget.setColumnWidth(_col, self.table_column_width[_col])

        # update size of summary table
        nbr_columns = self.ui.summary_table.columnCount()
        for _col in range(nbr_columns):
            self.ui.summary_table.setColumnWidth(_col, self.summary_table_width[_col])

        self.calibration_widgets = {'1': {'x0': self.ui.calibration1_x0,
                                          'y0': self.ui.calibration1_y0,
                                          'width': self.ui.calibration1_width,
                                          'height': self.ui.calibration1_height,
                                          'value': self.ui.calibration1_value,
                                          },
                                    '2': {'x0': self.ui.calibration2_x0,
                                          'y0': self.ui.calibration2_y0,
                                          'width': self.ui.calibration2_width,
                                          'height': self.ui.calibration2_height,
                                          'value': self.ui.calibration2_value,
                                          },
                                    }

        self.calibration_widgets_label = {'1': {'x0_label': self.ui.calibration1_x0_label,
                                                'y0_label': self.ui.calibration1_y0_label,
                                                'width_label': self.ui.calibration1_width_label,
                                                'height_label': self.ui.calibration1_height_label,
                                                'value_label': self.ui.calibration1_value_label,
                                                'group': self.ui.calibration1_groupbox,
                                                },
                                         '2': {'x0_label': self.ui.calibration2_x0_label,
                                               'y0_label': self.ui.calibration2_y0_label,
                                               'width_label': self.ui.calibration2_width_label,
                                               'height_label': self.ui.calibration2_height_label,
                                               'value_label': self.ui.calibration2_value_label,
                                               'group': self.ui.calibration2_groupbox,
                                              },
                                          }

        # will keep record of the x0, y0, width, height, value and color of the calibration rois
        self.calibration_roi = {'1': {},
                                '2': {},
                                }

        # init calibrated roi
        self.populate_calibration_widgets(calibration_index=1)
        self.populate_calibration_widgets(calibration_index=2)


    def populate_calibration_widgets(self, calibration_index=1):
        calibration_ui = self.calibration_widgets[str(calibration_index)]
        calibration_roi = self.calibrated_roi[str(calibration_index)]

        for _keys in calibration_ui.keys():
            calibration_ui[_keys].setText(str(calibration_roi[_keys]))

    def init_parameters(self):
        # init the position of the measurement ROI
        [height, width] = np.shape(self.data_dict['data'][0])
        self.default_measurement_roi['width'] = np.int(width/10)
        self.default_measurement_roi['height'] = np.int(height/10)
        self.default_measurement_roi['x0'] = np.int(width/2)
        self.default_measurement_roi['y0'] = np.int(height/2)

        self.calibrated_roi['2']['x0'] = width - self.calibrated_roi['2']['width']
        self.calibrated_roi['2']['y0'] = height - self.calibrated_roi['2']['height']

        self.calibrated_roi['1']['color'] = 'b' # blue
        self.calibrated_roi['2']['color'] = 'r' # red

    # main methods
    def display_image(self):
        """display the image selected by the file slider"""

        _image = self.get_image_selected()

        _view = self.ui.image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()

        first_update = False
        if self.histogram_level == []:
            first_update = True
        _histo_widget = self.ui.image_view.getHistogramWidget()
        self.histogram_level = _histo_widget.getLevels()

        _image = np.transpose(_image)
        self.ui.image_view.setImage(_image)
        self.live_image = _image
        _view_box.setState(_state)

        if not first_update:
            _histo_widget.setLevels(self.histogram_level[0], self.histogram_level[1])

        # calibrated and measurement ROIs
        self.display_roi()

    def display_roi(self):
        """display the calibrated and measurement rois"""

        # first we remove the calibrated rois
        for _roi_id in self.roi_ui_calibrated:
            self.ui.image_view.removeItem(_roi_id)

        if self.ui.use_calibration1_checkbox.isChecked():
            # yes, we have calibrated rois
            slider_index = self.ui.file_slider.value()

            # calibration1
            cal1_file_index = np.int(self.ui.calibration1_index.text())
            if slider_index == cal1_file_index:
                self.ui.image_view.addItem(self.roi_ui_calibrated[0])

        if self.ui.use_calibration2_checkbox.isChecked():
            # yes, we have calibrated rois
            slider_index = self.ui.file_slider.value()

            # calibration2
            cal2_file_index = np.int(self.ui.calibration2_index.text())
            if slider_index == cal2_file_index:
                self.ui.image_view.addItem(self.roi_ui_calibrated[1])

    def record_calibration(self, index=1):
        x0 = np.int(str(self.calibration_widgets[str(index)]['x0'].text()))
        y0 = np.int(str(self.calibration_widgets[str(index)]['y0'].text()))
        width = np.int(str(self.calibration_widgets[str(index)]['width'].text()))
        height = np.int(str(self.calibration_widgets[str(index)]['height'].text()))
        if np.isnan(np.float(str(self.calibration_widgets[str(index)]['value'].text()))):
            return

        value = np.float(str(self.calibration_widgets[str(index)]['value'].text()))

        if index == 1:
            file_index = np.int(str(self.ui.calibration1_index.text()))
        else:
            file_index = np.int(str(self.ui.calibration2_index.text()))

        _file_data = self.data_dict['data'][file_index]
        _region_data = _file_data[y0:y0+height, x0:x0+width]
        _mean = np.nanmean(_region_data)

        self.calibration[str(index)] = {}
        self.calibration[str(index)]['mean_counts'] = _mean
        self.calibration[str(index)]['value'] = value

    def calculate_measurement_profiles(self):
        """calculate for each measurement roi the mean counts using the calibrated regions. The
        value will be displayed in the summary table"""

        def ratio_calibration(cali_1=True, cali_2=True, input_value=np.NaN):
            if cali_1 and cali_2:
                cal1_mean = self.calibration['1']['mean_counts']
                cal1_value = self.calibration['1']['value']
                cal2_mean = self.calibration['2']['mean_counts']
                cal2_value = self.calibration['2']['value']
                return ((cal2_value - cal1_value)/(cal2_mean - cal1_mean)*(input_value - cal1_mean) + cal1_value)

            elif cali_1:
                index = '1'

            elif cali_2:
                index = '2'

            else:
                return input_value

            cali_mean = self.calibration[index]['mean_counts']
            cali_value = self.calibration[index]['value']
            return (input_value/cali_mean) * cali_value

        self.calibration = {} # reset
        cali_1 = self.ui.use_calibration1_checkbox.isChecked()
        cali_2 = self.ui.use_calibration2_checkbox.isChecked()
        if cali_1:
            self.record_calibration(index=1)
        if cali_2:
            self.record_calibration(index=2)

        nbr_row = self.ui.tableWidget.rowCount()
        measurement_dict = {}
        for _measurement_row in np.arange(nbr_row):
            (x0, y0, width, height) = self.get_item_row(row=_measurement_row)
            _measurement_data = []
            for _data_index, _data in enumerate(self.data_dict['data']):
                data_counts = np.nanmean(_data[y0:y0+height, x0:x0+width])

                real_data_counts = ratio_calibration(cali_1 = cali_1,
                                                     cali_2 = cali_2,
                                                     input_value = data_counts)

                item = QtGui.QTableWidgetItem("{:.2f}".format(real_data_counts))
                _measurement_data.append(real_data_counts)
                self.ui.summary_table.setItem(_data_index, _measurement_row+3, item)

            measurement_dict[str(_measurement_row+1)] = _measurement_data

        self.measurement_dict = measurement_dict

    def display_measurement_profiles(self, refresh_calculation=True):
        """will calculate the mean counts of the calibrated samples (if selected)
        and display the measurement mean of all the rois defined
        """
        self.ui.measurement_view.clear()
        try:
            self.ui.measurement_view.scene().removeItem(self.legend)
        except Exception as e:
            print(e)

        self.legend = self.ui.measurement_view.addLegend()

        if refresh_calculation:
            self.calculate_measurement_profiles()

        _color = Color()
        _color_list = _color.get_list_rgb(nbr_color=self.ui.tableWidget.rowCount())

        for _index, _key in enumerate(self.measurement_dict.keys()):
            _data = self.measurement_dict[_key]
            self.ui.measurement_view.plot(_data,
                                          name="Region {}".format(1+_index),
                                          pen=_color_list[_index])

    def remove_row(self, row=-1):
        if row == -1:
            return
        self.ui.tableWidget.removeRow(row)

        nbr_row = self.ui.tableWidget.rowCount()
        if row == nbr_row:
            row -= 1

        if nbr_row > 0:
            nbr_col = self.ui.tableWidget.columnCount()
            new_selection = QtGui.QTableWidgetSelectionRange(row, 0, row, nbr_col - 1)
            self.ui.tableWidget.setRangeSelected(new_selection, True)

    def insert_row(self, row=-1):
        if row == -1:
            row = 0

        self.ui.tableWidget.blockSignals(True)
        default_values = self.default_measurement_roi

        self.ui.tableWidget.insertRow(row)
        self.set_item_main_table(row=row, col=0, value=default_values['x0'])
        self.set_item_main_table(row=row, col=1, value=default_values['y0'])
        self.set_item_main_table(row=row, col=2, value=default_values['width'])
        self.set_item_main_table(row=row, col=3, value=default_values['height'])

        # select new entry
        nbr_row = self.ui.tableWidget.rowCount()
        nbr_col = self.ui.tableWidget.columnCount()
        full_range = QtGui.QTableWidgetSelectionRange(0, 0, nbr_row-1, nbr_col-1)
        self.ui.tableWidget.setRangeSelected(full_range, False)
        new_selection = QtGui.QTableWidgetSelectionRange(row, 0, row, nbr_col-1)
        self.ui.tableWidget.setRangeSelected(new_selection, True)
        self.ui.tableWidget.blockSignals(False)

    def insert_column_in_summary_table(self, roi_index=-1):
        col_offset = 3
        if roi_index == -1:
            roi_index = 0

        roi_index += col_offset
        self.ui.summary_table.insertColumn(roi_index)
        item = QtWidgets.QTableWidgetItem()
        self.ui.summary_table.setHorizontalHeaderItem(roi_index, item)
        self.renamed_summary_table_region_header()

    def remove_column_in_summary_table(self, roi_index=-1):
        col_offset = 3
        if roi_index == -1:
            roi_index = 0

        roi_index += col_offset
        self.ui.summary_table.removeColumn(roi_index)
        self.renamed_summary_table_region_header()

    def renamed_summary_table_region_header(self):
        # rename all the headers
        nbr_col = self.ui.summary_table.columnCount()
        if nbr_col <= 3:
            return

        _index = 1
        for _col in np.arange(3, nbr_col):
            item = self.ui.summary_table.horizontalHeaderItem(_col)
            item.setText("Region {}".format(_index))
            _index += 1

    def update_mean_counts(self, row=-1, all=False):
        if all == True:
            nbr_row = self.ui.tableWidget.rowCount()
            for _row in np.arange(nbr_row):
                self.update_mean_counts(row=_row)
        else:
            # FIXME
            pass

    def insert_measurement_roi_ui(self, row=-1):
        default_roi = self.default_measurement_roi
        new_roi = pg.RectROI([default_roi['x0'], default_roi['y0']],
                             [default_roi['height'], default_roi['width']],
                             pen='g')
        new_roi.addScaleHandle([1, 1], [0, 0])
        new_roi.addScaleHandle([0, 0], [1, 1])
        self.ui.image_view.addItem(new_roi)
        new_roi.sigRegionChanged.connect(self.measurement_roi_moved)
        self.roi_ui_measurement.insert(row, new_roi)

    def remove_measurement_roi_ui(self, row=-1):
        """roi_ui_measurement is where the ROI ui (pyqtgraph) are saved"""
        if row == -1:
            return
        old_roi = self.roi_ui_measurement[row]
        self.roi_ui_measurement.remove(old_roi)
        self.ui.image_view.removeItem(old_roi)

    def check_status_next_prev_image_button(self):
        """this will enable or not the prev or next button next to the slider file image"""
        current_slider_value = self.ui.file_slider.value()
        min_slider_value = self.ui.file_slider.minimum()
        max_slider_value = self.ui.file_slider.maximum()

        _prev = True
        _next = True

        if current_slider_value == min_slider_value:
            _prev = False
        elif current_slider_value == max_slider_value:
            _next = False

        self.ui.previous_image_button.setEnabled(_prev)
        self.ui.next_image_button.setEnabled(_next)

    def use_current_calibration_file(self, index=1):
        current_file_index = self.ui.file_slider.value()
        if index == 1:
            ui = self.ui.calibration1_index
        else:
            ui = self.ui.calibration2_index
        ui.setText(str(current_file_index))
        self.slider_file_changed(-1)

    def display_this_file(self, index=1):
        if index == 1:
            ui = self.ui.calibration1_index
        else:
            ui = self.ui.calibration2_index

        file_index = np.int(str(ui.text()))
        self.ui.file_slider.setValue(file_index)
        self.slider_file_changed(-1)

    def update_calibration_widgets(self, index=1):
        roi_ui = self.roi_ui_calibrated[index-1]
        region = roi_ui.getArraySlice(self.live_image,
                                      self.ui.image_view.imageItem)

        x0 = region[0][0].start
        x1 = region[0][0].stop
        y0 = region[0][1].start
        y1 = region[0][1].stop

        width = np.abs(x1 - x0)-1
        height = np.abs(y1 - y0)-1

        roi_widgets = self.calibration_widgets[str(index)]
        roi_widgets['x0'].setText(str(x0))
        roi_widgets['y0'].setText(str(y0))
        roi_widgets['width'].setText(str(width))
        roi_widgets['height'].setText(str(height))

        self.calibration_roi[str(index)]['x0'] = x0
        self.calibration_roi[str(index)]['y0'] = y0
        self.calibration_roi[str(index)]['width'] = width
        self.calibration_roi[str(index)]['height'] = height

    def calibration_widgets_changed(self, index=1):
        roi_ui = self.roi_ui_calibrated[index-1]
        widgets_ui = self.calibration_widgets[str(index)]
        x0 = np.int(widgets_ui['x0'].text())
        y0 = np.int(widgets_ui['y0'].text())
        width = np.int(widgets_ui['width'].text())
        height = np.int(widgets_ui['height'].text())

        roi_ui.setPos((x0, y0))
        roi_ui.setSize((width, height))

        calibration_roi = self.calibration_roi[str(index)]
        calibration_roi['x0'] = x0
        calibration_roi['y0'] = y0
        calibration_roi['height'] = height
        calibration_roi['width'] = width

    def update_all_measurement_rois_from_view(self):
        # reached when the ROIs are moved in the ui

        def get_roi_parameters(roi_ui):
            region = roi_ui.getArraySlice(self.live_image,
                                          self.ui.image_view.imageItem)
            x0 = region[0][0].start
            x1 = region[0][0].stop
            y0 = region[0][1].start
            y1 = region[0][1].stop
            width = np.abs(x1 - x0) - 1
            height = np.abs(y1 - y0) - 1

            return (x0, y0, width, height)

        list_roi  = self.roi_ui_measurement
        for _row, _roi in enumerate(list_roi):
            [x0, y0, width, height] = get_roi_parameters(_roi)
            self.ui.tableWidget.item(_row, 0).setText(str(x0))
            self.ui.tableWidget.item(_row, 1).setText(str(y0))
            self.ui.tableWidget.item(_row, 2).setText(str(width))
            self.ui.tableWidget.item(_row, 3).setText(str(height))

    def update_measurement_rois_from_table(self, row=0):
        roi_ui = self.roi_ui_measurement[row]
        [x0, y0, width, height] = self.get_item_row(row=row)
        roi_ui.blockSignals(True)
        roi_ui.setPos((x0, y0))
        roi_ui.setSize((width, height))
        roi_ui.blockSignals(False)

    # setter
    def set_item_main_table(self, row=0, col=0, value=''):
        item = QtGui.QTableWidgetItem(str(value))
        self.ui.tableWidget.setItem(row, col, item)
        if col == 4:
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

    def set_item_summary_table(self, row=0, col=0, value=''):
        item = QtGui.QTableWidgetItem(str(value))
        self.ui.summary_table.setItem(row, col, item)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

    # getter
    def get_image_selected(self):
        slider_index = self.ui.file_slider.value()
        _image = self.data_dict['data'][slider_index]
        return _image

    def get_selected_row(self):
        selection = self.ui.tableWidget.selectedRanges()
        if selection:
            top_row = selection[0].topRow()
            return top_row
        else:
            return -1

    def get_item_row(self, row=0):
        x0 = np.int(str(self.ui.tableWidget.item(row, 0).text()))
        y0 = np.int(str(self.ui.tableWidget.item(row, 1).text()))
        width = np.int(str(self.ui.tableWidget.item(row, 2).text()))
        height = np.int(str(self.ui.tableWidget.item(row, 3).text()))
        return (x0, y0, width, height)

    def change_slider(self, offset=+1):
        self.ui.file_slider.blockSignals(True)
        current_slider_value = self.ui.file_slider.value()
        new_row_selected = current_slider_value + offset
        self.ui.file_slider.setValue(new_row_selected)
        self.check_status_next_prev_image_button()
        self.display_image()
        self.ui.file_slider.blockSignals(False)

    def calibration_widgets_handler(self, status, index=1):
        list_ui = self.calibration_widgets[str(index)]
        for _ui in list_ui.keys():
            list_ui[_ui].setEnabled(status)

        list_ui = self.calibration_widgets_label[str(index)]
        for _ui in list_ui.keys():
            list_ui[_ui].setEnabled(status)

    def calibration1_widgets_handler(self, status):
        self.calibration_widgets_handler(status, index=1)

    def calibration2_widgets_handler(self, status):
        self.calibration_widgets_handler(status, index=2)

    # event handler
    def calibration1_widgets_changed(self):
        self.calibration_widgets_changed(index=1)
        self.display_measurement_profiles()

    def calibration2_widgets_changed(self):
        self.calibration_widgets_changed(index=2)
        self.display_measurement_profiles()

    def display_this_cal1_file(self):
        self.display_this_file(index=1)

    def display_this_cal2_file(self):
        self.display_this_file(index=2)

    def use_current_calibration1_file(self):
        self.use_current_calibration_file(index=1)
        self.display_measurement_profiles()

    def use_current_calibration2_file(self):
        self.use_current_calibration_file(index=2)
        self.display_measurement_profiles()

    def measurement_roi_moved(self):
        self.update_all_measurement_rois_from_view()
        self.display_measurement_profiles()

    def calibration1_roi_moved(self):
        self.update_calibration_widgets(index=1)
        self.display_measurement_profiles()

    def calibration2_roi_moved(self):
        self.update_calibration_widgets(index=2)
        self.display_measurement_profiles()

    def use_calibration1_checked(self):
        cali_button_checked = self.ui.use_calibration1_checkbox.isChecked()
        self.calibration1_widgets_handler(cali_button_checked)
        self.slider_file_changed(-1)
        self.display_measurement_profiles()

    def use_calibration2_checked(self):
        cali_button_checked = self.ui.use_calibration2_checkbox.isChecked()
        self.calibration2_widgets_handler(cali_button_checked)
        self.slider_file_changed(-1)
        self.display_measurement_profiles()

    def slider_file_changed(self, index_selected):
        self.display_image()
        slider_value = self.ui.file_slider.value()
        self.ui.image_slider_value.setText(str(slider_value))
        self.check_status_next_prev_image_button()
        self.display_measurement_profiles()

    def add_row_button_clicked(self):
        selected_row = self.get_selected_row()
        self.insert_row(row=selected_row)
        self.insert_column_in_summary_table(roi_index=selected_row)
        self.insert_measurement_roi_ui(row=selected_row)
        self.update_mean_counts(row=selected_row)
        self.display_measurement_profiles()

    def remove_row_button_clicked(self):
        selected_row = self.get_selected_row()
        self.remove_row(row=selected_row)
        self.remove_column_in_summary_table(roi_index=selected_row)
        self.remove_measurement_roi_ui(row=selected_row)
        self.display_measurement_profiles()

    def cell_changed(self, row, col ):
        self.update_measurement_rois_from_table(row=row)
        self.display_measurement_profiles()

    def export_button_clicked(self):
        _export_folder = QFileDialog.getExistingDirectory(self,
                                                          directory=self.working_dir,
                                                          caption = "Select Output Folder",
                                                          options=QFileDialog.ShowDirsOnly)
        if _export_folder:
            o_export = ExportCalibration(parent = self,
                                         export_folder = _export_folder)
            o_export.run()
            QtGui.QGuiApplication.processEvents()

    def previous_image_button_clicked(self):
        self.change_slider(offset = -1)
        self.display_measurement_profiles()

    def next_image_button_clicked(self):
        self.change_slider(offset = +1)
        self.display_measurement_profiles()

    def help_button_clicked(self):
        import webbrowser
        webbrowser.open("https://neutronimaging.pages.ornl.gov/en/tutorial/notebooks/registration/")

    def closeEvent(self, event=None):
        pass


class ExportCalibration(object):

    def __init__(self, parent=None, export_folder=''):
        self.parent = parent
        self.export_folder = export_folder

    def get_metadata(self):
        metadata = []
        metadata.append("#Working dir: {}".format(self.parent.working_dir))
        if self.parent.ui.use_calibration1_checkbox.isChecked():
            metadata.append("#Calibration Region 1:")
            metadata.append("#   x0: {}".format(str(self.parent.ui.calibration1_x0.text())))
            metadata.append("#   y0: {}".format(str(self.parent.ui.calibration1_y0.text())))
            metadata.append("#   width: {}".format(str(self.parent.ui.calibration1_width.text())))
            metadata.append("#   height: {}".format(str(self.parent.ui.calibration1_height.text())))
            metadata.append("#   file index: {}".format(str(self.parent.ui.calibration1_index.text())))
            metadata.append("#   value requested: {}".format(str(self.parent.ui.calibration1_value.text())))
        if self.parent.ui.use_calibration2_checkbox.isChecked():
            metadata.append("#Calibration Region 2:")
            metadata.append("#   x0: {}".format(str(self.parent.ui.calibration2_x0.text())))
            metadata.append("#   y0: {}".format(str(self.parent.ui.calibration2_y0.text())))
            metadata.append("#   width: {}".format(str(self.parent.ui.calibration2_width.text())))
            metadata.append("#   height: {}".format(str(self.parent.ui.calibration2_height.text())))
            metadata.append("#   file index: {}".format(str(self.parent.ui.calibration2_index.text())))
            metadata.append("#   value requested: {}".format(str(self.parent.ui.calibration2_value.text())))
        nbr_measurement_region = self.parent.ui.tableWidget.rowCount()
        _legend = "#File_name, Time_stamp, Relative_time(s)"
        if nbr_measurement_region > 0:
            metadata.append("#Measurement Regions:")
            for _index_region in np.arange(nbr_measurement_region):
                [x0, y0, width, height] = self.parent.get_item_row(row=_index_region)
                metadata.append("#  region {}: [x0, y0, width, height]=[{}, {}, {}, {}]".format(_index_region,
                                                                                                x0, y0,
                                                                                                width, height))
                _legend += ", Mean_counts_of_region {}".format(_index_region+1)
        metadata.append("#")
        metadata.append(_legend)
        return metadata

    def run(self):
        nbr_files = self.parent.ui.summary_table.rowCount()
        nbr_col= self.parent.ui.summary_table.columnCount()

        metadata = self.get_metadata()
        data = []
        for _row in np.arange(nbr_files):
            _row_str = []
            for _col in np.arange(nbr_col):
                _row_str.append(str(self.parent.ui.summary_table.item(_row, _col).text()))
            data.append(",".join(_row_str))

        export_file_name = os.path.basename(self.parent.working_dir)
        full_export_file_name = os.path.join(self.export_folder, export_file_name + "_calibrated_transmission.txt")

        make_ascii_file(metadata=metadata,
                        data=data,
                        output_file_name=full_export_file_name,
                        dim='1d')

        QtGui.QApplication.processEvents()

        # display name of file exported for 10s
        self.parent.ui.statusbar.showMessage("File Created: {}".format(full_export_file_name), 10000)
