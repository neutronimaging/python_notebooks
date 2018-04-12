import ipywe.fileselector

from IPython.core.display import HTML
from IPython.core.display import display
from ipywidgets import widgets

import numpy as np
import os
from skimage import transform
from scipy.ndimage.interpolation import shift
from skimage.feature import register_translation
import copy

import pprint

import pyqtgraph as pg
from pyqtgraph.dockarea import *

from __code.color import  Color

try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtGui import QMainWindow, QDialog
except ImportError:
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog

from NeuNorm.normalization import Normalization


from __code.ui_registration  import Ui_MainWindow as UiMainWindow
from __code.ui_registration_tool import Ui_MainWindow as UiMainWindowTool
from __code.ui_registration_auto_confirmation import Ui_Dialog as UiDialog
from __code.ui_registration_markers import Ui_Dialog as UiDialogMarkers


class RegistrationUi(QMainWindow):

    table_registration = {} # dictionary that populate the table

    table_column_width = [650, 80, 80, 80]

    # image view
    histogram_level = []

    # by default, the reference image is the first image
    reference_image_index = 0
    reference_image = []
    color_reference_background = QtGui.QColor(50, 250, 50)
    color_reference_profile = [50, 250, 50]

    # image currently display in image_view
    live_image = []

    # grid on top of images
    grid_view = {'pos': None,
                 'adj': None,
                 'item': None,
                 'color': (0, 0, 255, 255, 1)}

    new_reference_image = True
    list_rgb_profile_color = []

    # external registration ui
    registration_tool_ui = None
    registration_auto_confirmation_ui = None
    registration_markers_ui = None

    # markers table
    # markers_table = {'1': {'data': {'file_0': {'x': 0, 'y':10, 'marker_ui': None},
    #                                 'file_1': {'x': 0, 'y':10, 'marker_ui': None},
    #                                 'file_2': {'x': 0, 'y':10, 'marker_ui': None},
    #                                   ... },
    #                        'ui': None,
    #                        'color': {'qpen': None,
    #                                  'name': ""},
    #                 {'2': .... }
    markers_table = {}

    markers_table_column_width = [330, 50, 50]

    def __init__(self, parent=None, data_dict=None):

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
            (maybe hidden behind this browser!)</span>'))

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Registration")

        self.data_dict = data_dict # Normalization data dictionary  {'filename': [],
                                                                     #'data': [[...],[...]]],
                                                                     #'metadata': [],
                                                                     #'shape': {}}

        # untouched array of images (used to move and rotate images)
        self.data_dict_raw = copy.deepcopy(data_dict)
        self.reference_image = self.data_dict['data'][self.reference_image_index]
        self.working_dir = os.path.basename(self.data_dict['file_name'][0])

        # initialization
        self.init_pyqtgrpah()
        self.init_widgets()
        self.init_table()
        self.init_parameters()
        self.init_statusbar()

        # display line profile
        self.profile_line_moved()

        self.new_reference_image = False
        self.ui.selection_reference_opacity_groupBox.setVisible(False) # because by default first row = reference selected

    # initialization
    def init_statusbar(self):
        self.eventProgress = QtGui.QProgressBar(self.ui.statusbar)
        self.eventProgress.setMinimumSize(300, 20)
        self.eventProgress.setMaximumSize(300, 20)
        self.eventProgress.setVisible(False)
        self.ui.statusbar.addPermanentWidget(self.eventProgress)

    def init_parameters(self):
        nbr_files = len(self.data_dict['file_name'])
        _color = Color()
        self.list_rgb_profile_color = _color.get_list_rgb(nbr_color=nbr_files)

        o_marker = MarkerDefaultSettings(image_reference=self.reference_image)
        self.o_MarkerDefaultSettings = o_marker

    def init_pyqtgrpah(self):

        area = DockArea()
        area.setVisible(True)
        d1 = Dock("Registered Image", size=(400, 600))
        d2 = Dock("Profile", size=(400, 200))

        area.addDock(d1, 'top')
        area.addDock(d2, 'bottom')

        # registered image
        self.ui.image_view = pg.ImageView(view=pg.PlotItem())
        self.ui.image_view.ui.menuBtn.hide()
        self.ui.image_view.ui.roiBtn.hide()
        # profile selection tool
        self.ui.profile_line = pg.LineSegmentROI([[50, 50], [100, 100]], pen='r')
        self.ui.image_view.addItem(self.ui.profile_line)
        d1.addWidget(self.ui.image_view)
        self.ui.profile_line.sigRegionChanged.connect(self.profile_line_moved)

        # profile
        self.ui.profile = pg.PlotWidget(title='Profile')
        self.ui.profile.plot()
        self.legend = self.ui.profile.addLegend()
        d2.addWidget(self.ui.profile)

        # set up layout
        vertical_layout = QtGui.QVBoxLayout()
        vertical_layout.addWidget(area)

        self.ui.pyqtgraph_widget.setLayout(vertical_layout)

    def init_widgets(self):
        """size and label of any widgets"""
        self.ui.splitter_2.setSizes([800, 100])

        # update size of table columns
        nbr_columns = self.ui.tableWidget.columnCount()
        for _col in range(nbr_columns):
            self.ui.tableWidget.setColumnWidth(_col, self.table_column_width[_col])

        # update slidewidget of files
        nbr_files = len(self.data_dict['file_name'])
        self.ui.file_slider.setMinimum(0)
        self.ui.file_slider.setMaximum(nbr_files-1)

        # selected image
        reference_image = self.data_dict['file_name'][0]
        self.ui.reference_image_label.setText(reference_image)

        # selection slider
        self.ui.selection_groupBox.setVisible(False)
        self.ui.next_image_button.setEnabled(True)

        # selected vs reference slider
        self.ui.selection_reference_opacity_groupBox.setVisible(False) # because by default first row = reference selected

    def init_table(self):
        """populate the table with list of file names and default xoffset, yoffset and rotation"""
        list_file_names = self.data_dict['file_name']
        table_registration = {}

        _row_index = 0
        for _file_index, _file in enumerate(list_file_names):

            _row_infos = {}

            # col 0 - file name
            _row_infos['filename'] = _file
            _row_infos['xoffset'] = 0
            _row_infos['yoffset'] = 0
            _row_infos['rotation'] = 0

            table_registration[_row_index] = _row_infos
            _row_index += 1

        self.table_registration = table_registration
        self.populate_table()

        #select first row
        self.select_row_in_table(0)

    def display_markers(self, all=False):
        if self.registration_markers_ui is None:
            return

        if all is False:
            _current_tab = self.registration_markers_ui.ui.tabWidget.currentIndex()
            _tab_title = self.registration_markers_ui.ui.tabWidget.tabText(_current_tab)
            self.display_markers_of_tab(marker_name=_tab_title)
        else:
            for _index, _marker_name in enumerate(self.markers_table.keys()):
                self.display_markers_of_tab(marker_name=_marker_name)

    def get_list_short_file_selected(self):
        list_row_selected = self.get_list_row_selected()
        full_list_files = np.array(self.data_dict['file_name'])
        list_file_selected = full_list_files[list_row_selected]
        list_short_file_selected = [os.path.basename(_file) for _file in
                                    list_file_selected]
        return list_short_file_selected

    def display_markers_of_tab(self, marker_name=''):
        self.close_markers_of_tab(marker_name=marker_name)
        # get short name of file selected
        list_short_file_selected = self.get_list_short_file_selected()
        pen = self.markers_table[marker_name]['color']['qpen']
        for _file in list_short_file_selected:
            _marker_data = self.markers_table[marker_name]['data'][_file]

            x = _marker_data['x']
            y = _marker_data['y']
            width = MarkerDefaultSettings.width
            height = MarkerDefaultSettings.height

            _marker_ui = pg.RectROI([x,y], [width, height], pen=pen)
            self.ui.image_view.addItem(_marker_ui)
            _marker_ui.removeHandle(0)
            _marker_ui.sigRegionChanged.connect(self.marker_has_been_moved)
            _marker_data['marker_ui'] = _marker_ui

    def marker_has_been_moved(self):
        list_short_file_selected = self.get_list_short_file_selected()
        for _index, _marker_name in enumerate(self.markers_table.keys()):
            for _file in list_short_file_selected:
                _marker_data = self.markers_table[_marker_name]['data'][_file]
                marker_ui = _marker_data['marker_ui']

                region = marker_ui.getArraySlice(self.live_image,
                                                 self.ui.image_view.imageItem)

                x0 = region[0][0].start
                y0 = region[0][1].start

                self.markers_table[_marker_name]['data'][_file]['x'] = x0
                self.markers_table[_marker_name]['data'][_file]['y'] = y0

                self.registration_markers_ui.update_markers_table_entry(marker_name=_marker_name,
                                                                        file=_file)


    def close_markers_of_tab(self, marker_name=''):
        _data = self.markers_table[marker_name]['data']
        for _file in _data:
            _marker_ui = _data[_file]['marker_ui']
            if _marker_ui:
                self.ui.image_view.removeItem(_marker_ui)

    def close_all_markers(self):
        for marker in self.markers_table.keys():
            self.close_markers_of_tab(marker_name = marker)

    def modified_images(self, list_row=[]):
        """using data_dict_raw images, will apply offset and rotation parameters
        and will save them in data_dict for plotting"""

        data_raw = self.data_dict_raw['data'].copy()
        for _row in list_row:

            xoffset = np.int(np.float(self.ui.tableWidget.item(_row, 1).text()))
            yoffset = np.int(np.float(self.ui.tableWidget.item(_row, 2).text()))
            rotate_angle = np.float(self.ui.tableWidget.item(_row, 3).text())

            _data = data_raw[_row].copy()
            _data  = transform.rotate(_data, rotate_angle)
            _data = shift(_data, (yoffset, xoffset), )

            self.data_dict['data'][_row] = _data

    def _intermediates_points(self, p1, p2):
        """"Return a list of nb_points equally spaced points
        between p1 and p2

        p1 = [x0, y0]
        p2 = [x1, y1]
        """

        # nb_points ?
        nb_points = np.int(3 * max([np.abs(p1[0] - p2[0]), np.abs(p2[1] - p1[1])]))

        x_spacing = (p2[0] - p1[0]) / (nb_points + 1)
        y_spacing = (p2[1] - p1[1]) / (nb_points + 1)

        full_array = [[np.int(p1[0] + i * x_spacing), np.int(p1[1] + i * y_spacing)]
                      for i in range(1, nb_points + 1)]

        clean_array = []
        for _points in full_array:
            if _points in clean_array:
                continue
            clean_array.append(_points)

        return clean_array

    def profile_line_moved(self):
        """update profile plot"""
        if self.live_image == []:
            return

        self.ui.profile.clear()
        try:
            self.ui.profile.scene().removeItem(self.legend)
        except Exception as e:
            print(e)

        self.legend = self.ui.profile.addLegend()

        region = self.ui.profile_line.getArraySlice(self.live_image,
                                                    self.ui.image_view.imageItem)

        x0 = region[0][0].start + 3
        x1 = region[0][0].stop - 3
        y0 = region[0][1].start + 3
        y1 = region[0][1].stop - 3

        p1 = [x0, y0]
        p2 = [x1, y1]

        intermediate_points = self._intermediates_points(p1, p2)
        xaxis = np.arange(len(intermediate_points))

        # profiles selected
        # if only one row selected !
        if self.ui.selection_groupBox.isVisible():

            if self.ui.selection_all.isChecked():
                min_row = np.int(self.ui.opacity_selection_slider.minimum()/100)
                max_row = np.int(self.ui.opacity_selection_slider.maximum()/100)

                for _index in np.arange(min_row, max_row+1):
                    if _index == self.reference_image_index:
                        continue

                    _data = np.transpose(self.data_dict['data'][_index])
                    _filename = os.path.basename(self.data_dict['file_name'][_index])
                    _profile = [_data[_point[0], _point[1]] for _point in intermediate_points]
                    self.ui.profile.plot(xaxis, _profile,
                                         name=_filename,
                                         pen=self.list_rgb_profile_color[_index])

            else: # selection slider
                slider_index = self.ui.opacity_selection_slider.sliderPosition() / 100
                from_index = np.int(slider_index)
                _data = np.transpose(self.data_dict['data'][from_index])
                _filename = os.path.basename(self.data_dict['file_name'][from_index])
                _profile = [_data[_point[0], _point[1]] for _point in intermediate_points]
                self.ui.profile.plot(xaxis,
                                     _profile,
                                     name=_filename,
                                     pen=self.list_rgb_profile_color[from_index])

                if from_index == slider_index:
                    pass

                else:
                    to_index = np.int(slider_index + 1)
                    _data = np.transpose(self.data_dict['data'][to_index])
                    _filename = os.path.basename(self.data_dict['file_name'][to_index])
                    _profile = [_data[_point[0], _point[1]] for _point in intermediate_points]
                    self.ui.profile.plot(xaxis,
                                         _profile,
                                         name=_filename,
                                         pen=self.list_rgb_profile_color[to_index])

        else:

            table_selection = self.ui.tableWidget.selectedRanges()
            if not table_selection == []:

                table_selection = table_selection[0]
                row_selected = table_selection.topRow()

                if not row_selected == self.reference_image_index:
                    _data = np.transpose(self.data_dict['data'][row_selected])
                    _filename = os.path.basename(self.data_dict['file_name'][row_selected])
                    _profile = [_data[_point[0], _point[1]] for _point in intermediate_points]
                    self.ui.profile.plot(xaxis,
                                         _profile,
                                         name=_filename,
                                         pen=self.list_rgb_profile_color[row_selected])


        # selected_image = self.live_image
        # profile_selected = [selected_image[_point[0],
        #                                    _point[1]] for _point in intermediate_points]
        #
        # self.ui.profile.plot(xaxis, profile_selected, name='Selected Image')


        # Always display profile reference
        reference_image = np.transpose(self.reference_image)
        profile_reference = [reference_image[_point[0],
                                             _point[1]] for _point in intermediate_points]

        reference_file_name = os.path.basename(self.data_dict['file_name'][self.reference_image_index])
        self.ui.profile.plot(xaxis, profile_reference,
                             pen=self.color_reference_profile,
                             name='Ref.: {}'.format(reference_file_name))

    def populate_table(self):
        """populate the table using the table_registration dictionary"""
        self.ui.tableWidget.blockSignals(True)
        table_registration = self.table_registration
        for _row in table_registration.keys():
            _row_infos = table_registration[_row]
            self.__insert_table_row(infos=_row_infos, row=_row)
        self.ui.tableWidget.blockSignals(False)

    def refresh_table(self):
        """refresh table contain by removing first everything before repopulating it"""
        self.__clear_table()
        self.populate_table()

    def __clear_table(self):
        nbr_row = self.ui.tableWidget.rowCount()
        for _row in np.arange(nbr_row):
            self.ui.tableWidget.removeRow(0)

    def __insert_table_row(self, infos={}, row=-1):
        self.ui.tableWidget.insertRow(row)

        is_reference_image = False
        if row == self.reference_image_index:
            is_reference_image = True

        self.set_item(row, 0, infos['filename'], is_reference_image=is_reference_image)
        self.set_item(row, 1, infos['xoffset'], is_reference_image=is_reference_image)
        self.set_item(row, 2, infos['yoffset'], is_reference_image=is_reference_image)
        self.set_item(row, 3, infos['rotation'], is_reference_image=is_reference_image)

    def set_item(self, row=0, col=0, value='', is_reference_image=False):
        item = QtGui.QTableWidgetItem(str(value))
        self.ui.tableWidget.setItem(row, col, item)
        if is_reference_image:
            item.setBackground(self.color_reference_background)
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

    def get_image_selected(self):
        """to get the image iselected, we will use the table selection as the new version
        allows several rows"""
        # index_selected = self.ui.file_slider.value()

        table_selection = self.ui.tableWidget.selectedRanges()
        if table_selection == []:
            return []

        table_selection = table_selection[0]
        top_row = table_selection.topRow()   # offset because first image is reference image
        bottom_row = table_selection.bottomRow() + 1

        _image = np.mean(self.data_dict['data'][top_row:bottom_row], axis=0)
        return _image

    def display_image(self):

        # if more than one row selected !
        if self.ui.selection_groupBox.isVisible():
            # if all selected
            if self.ui.selection_all.isChecked():
                _image = self.get_image_selected()
            else:  # display selected images according to slider position

                # retrieve slider infos
                slider_index = self.ui.opacity_selection_slider.sliderPosition() / 100

                from_index = np.int(slider_index)
                to_index = np.int(slider_index + 1)

                if from_index == slider_index:
                    _image = self.data_dict['data'][from_index]
                else:
                    _from_image = self.data_dict['data'][from_index]

                    _to_image = self.data_dict['data'][to_index]

                    _from_coefficient = np.abs(to_index - slider_index)
                    _to_coefficient = np.abs(slider_index - from_index)
                    _image = _from_image * _from_coefficient + _to_image * _to_coefficient

        else: # only 1 row selected
            _image = self.get_image_selected()

        if _image == []: # display only reference image
            self.display_only_reference_image()
            return

        self.ui.selection_reference_opacity_groupBox.setVisible(True)

        _view = self.ui.image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()

        first_update = False
        if self.histogram_level == []:
            first_update = True
        _histo_widget = self.ui.image_view.getHistogramWidget()
        self.histogram_level = _histo_widget.getLevels()

        _opacity_coefficient = self.ui.opacity_slider.value()  # betwween 0 and 100
        _opacity_image = _opacity_coefficient / 100.
        _image = np.transpose(_image) * _opacity_image

        _opacity_selected = 1 - _opacity_image
        _reference_image = np.transpose(self.reference_image) * _opacity_selected

        _final_image = _reference_image + _image
        self.ui.image_view.setImage(_final_image)
        self.live_image = _final_image
        _view_box.setState(_state)

        if not first_update:
            _histo_widget.setLevels(self.histogram_level[0], self.histogram_level[1])

    def calculate_matrix_grid(self, grid_size=1, height=1, width=1):
        """calculate the matrix that defines the vertical and horizontal lines
        that allow pyqtgraph to display the grid"""

        pos_adj_dict = {}

        # pos - each matrix defines one side of the line
        pos = []
        adj = []

        # vertical lines
        x = 0
        index = 0
        while (x <= width):
            one_edge = [x, 0]
            other_edge = [x, height]
            pos.append(one_edge)
            pos.append(other_edge)
            adj.append([index, index+1])
            x += grid_size
            index += 2

        # vertical lines
        y = 0
        while (y <= height):
            one_edge = [0, y]
            other_edge = [width, y]
            pos.append(one_edge)
            pos.append(other_edge)
            adj.append([index, index+1])
            y += grid_size
            index += 2

        pos_adj_dict['pos'] = np.array(pos)
        pos_adj_dict['adj'] = np.array(adj)

        return pos_adj_dict

    def display_live_image(self):
        """no calculation will be done. This will only display the reference image
        but will display or not the grid on top"""
        live_image = self.live_image

        _view = self.ui.image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()
        first_update = False
        if self.histogram_level == []:
            first_update = True
        _histo_widget = self.ui.image_view.getHistogramWidget()
        self.histogram_level = _histo_widget.getLevels()

        self.ui.image_view.setImage(live_image)

        _view_box.setState(_state)
        if not first_update:
            _histo_widget.setLevels(self.histogram_level[0],
                                    self.histogram_level[1])

        # we do not want a grid on top
        if self.grid_view['item']:
            self.ui.image_view.removeItem(self.grid_view['item'])

        if not self.ui.grid_display_checkBox.isChecked():
            return

        grid_size = self.ui.grid_size_slider.value()
        [height, width] = np.shape(live_image)

        pos_adj_dict = self.calculate_matrix_grid(grid_size=grid_size,
                                                  height=height,
                                                  width=width)
        pos = pos_adj_dict['pos']
        adj = pos_adj_dict['adj']

        line_color = self.grid_view['color']
        lines = np.array([line_color for n in np.arange(len(pos))],
                         dtype=[('red', np.ubyte), ('green', np.ubyte),
                                ('blue', np.ubyte), ('alpha', np.ubyte),
                                ('width', float)])


        grid = pg.GraphItem()
        self.ui.image_view.addItem(grid)
        grid.setData(pos=pos,
                     adj=adj,
                     pen=lines,
                     symbol=None,
                     pxMode=False)
        self.grid_view['item'] = grid


    def display_only_reference_image(self):

        self.ui.selection_reference_opacity_groupBox.setVisible(False)

        _view = self.ui.image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()

        first_update = False
        if self.histogram_level == []:
            first_update = True
        _histo_widget = self.ui.image_view.getHistogramWidget()
        self.histogram_level = _histo_widget.getLevels()

        _image = np.transpose(self.reference_image)
        self.ui.image_view.setImage(_image)
        self.live_image = _image
        _view_box.setState(_state)

        if not first_update:
            _histo_widget.setLevels(self.histogram_level[0], self.histogram_level[1])

    def select_row_in_table(self, row=0):
        nbr_col = self.ui.tableWidget.columnCount()
        nbr_row = self.ui.tableWidget.rowCount()

        # clear previous selection
        full_range = QtGui.QTableWidgetSelectionRange(0, 0, nbr_row-1, nbr_col-1)
        self.ui.tableWidget.setRangeSelected(full_range, False)

        # select file of interest
        selection_range = QtGui.QTableWidgetSelectionRange(row, 0, row, nbr_col-1)
        self.ui.tableWidget.setRangeSelected(selection_range, True)

        self.ui.tableWidget.showRow(row)

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

    def change_slider(self, offset=+1):
        self.ui.file_slider.blockSignals(True)
        current_slider_value = self.ui.file_slider.value()
        new_row_selected = current_slider_value + offset
        self.select_row_in_table(row=new_row_selected)
        self.ui.file_slider.setValue(new_row_selected)
        self.check_status_next_prev_image_button()
        self.display_image()
        self.profile_line_moved()
        self.ui.file_slider.blockSignals(False)

    def check_selection_slider_status(self):
        """
        if there is more than one row selected, we need to display the left slider but also
        we need to disable the next, prev buttons and file index slider
        """
        selection = self.ui.tableWidget.selectedRanges()
        if selection:

            list_file_index_widgets = [self.ui.previous_image_button,
                                       self.ui.file_slider,
                                       self.ui.next_image_button]

            top_row = selection[0].topRow()
            bottom_row = selection[0].bottomRow()
            if np.abs(bottom_row - top_row) >= 1: # show selection images widgets
                self.ui.selection_groupBox.setVisible(True)
                self.ui.top_row_label.setText("Row {}".format(top_row+1))
                self.ui.bottom_row_label.setText("Row {}".format(bottom_row+1))
                self.ui.opacity_selection_slider.setMinimum(top_row*100)
                self.ui.opacity_selection_slider.setMaximum(bottom_row*100)
                self.ui.opacity_selection_slider.setSliderPosition(top_row*100)
                _file_index_status = False
            else:
                self.ui.selection_groupBox.setVisible(False)
                _file_index_status = True

            for _widget in list_file_index_widgets:
                _widget.setVisible(_file_index_status)

    # Utilities

    def get_list_row_selected(self):
        table_selection = self.ui.tableWidget.selectedRanges()

        # that means we selected the first row
        if table_selection == []:
            return [0]

        table_selection = table_selection[0]
        top_row = table_selection.topRow()
        bottom_row = table_selection.bottomRow() + 1

        return np.arange(top_row, bottom_row)

    def check_registration_tool_widgets(self):
        """if the registration tool is active, and the reference image is the only row selected,
        disable the widgets"""
        if self.registration_tool_ui:
            self.registration_tool_ui.update_status_widgets()

    def set_widget_status(self, list_ui=[], enabled=True):
        for _ui in list_ui:
            _ui.setEnabled(enabled)

    # Event handler

    def opacity_changed(self, opacity_value):
        self.display_image()

    def table_row_clicked(self):
        self.ui.file_slider.blockSignals(True)
        row = self.ui.tableWidget.currentRow()
        self.ui.file_slider.setValue(row)
        self.display_image()
        self.check_selection_slider_status()
        self.profile_line_moved()
        self.check_selection_slider_status()
        self.check_status_next_prev_image_button()
        self.check_registration_tool_widgets()
        self.display_markers(all=True)
        self.ui.file_slider.blockSignals(False)

    def table_cell_modified(self, row, column):
        list_row_selected = self.get_list_row_selected()
        self.modified_images(list_row=list_row_selected)
        self.display_image()
        self.profile_line_moved()

    def slider_file_changed(self, index_selected):
        self.ui.tableWidget.blockSignals(True)
        self.select_row_in_table(row=index_selected)
        self.display_image()
        self.profile_line_moved()
        self.check_status_next_prev_image_button()
        self.ui.tableWidget.blockSignals(False)

    def help_button_clicked(self):
        import webbrowser
        webbrowser.open("https://neutronimaging.pages.ornl.gov/en/tutorial/notebooks/registration/")

    def ok_button_clicked(self):
        self.close()

    def export_button_clicked(self):
        _export_folder = QFileDialog.getExistingDirectory(self,
                                                          directory=self.working_dir,
                                                          caption = "Select Output Folder",
                                                          options=QFileDialog.ShowDirsOnly)
        if _export_folder:
            o_export = ExportRegistration(parent=self, export_folder=_export_folder)
            o_export.run()
            QtGui.QApplication.processEvents()

    def closeEvent(self, event=None):
        if self.registration_tool_ui:
            self.registration_tool_ui.close()
        if self.registration_markers_ui:
            self.registration_markers_ui.close()

    def previous_image_button_clicked(self):
        self.change_slider(offset = -1)

    def next_image_button_clicked(self):
        self.change_slider(offset = +1)

    def selection_all_clicked(self):
        _is_checked = self.ui.selection_all.isChecked()

        list_widgets = [self.ui.top_row_label,
                        self.ui.bottom_row_label,
                        self.ui.opacity_selection_slider]
        for _widget in list_widgets:
            _widget.setEnabled(not _is_checked)
        self.display_image()
        self.profile_line_moved()

    def selection_slider_changed(self):
        # self.update_selection_images()
        self.display_image()
        self.profile_line_moved()

    def selection_slider_moved(self):
        # self.update_selection_images()
        self.display_image()
        self.profile_line_moved()

    def manual_registration_button_clicked(self):
        """launch the manual registration tool"""
        o_registration_tool = RegistrationManualLauncher(parent=self)
        self.set_widget_status(list_ui=[self.ui.auto_registration_button],
                           enabled=False)

    def auto_registration_button_clicked(self):
        o_registration_auto_confirmed = RegistrationAutoConfirmationLauncher(parent=self)

    def markers_registration_button_clicked(self):
        o_markers_registration = RegistrationMarkersLauncher(parent=self)
        self.set_widget_status(list_ui=[self.ui.auto_registration_button],
                           enabled=False)

    def start_auto_registration(self):
        o_auto_register = RegistrationAuto(parent=self,
                                           reference_image=self.reference_image,
                                           floating_images=self.data_dict['data'])
        o_auto_register.auto_align()

    def grid_display_checkBox_clicked(self):
        self.display_live_image()

    def grid_size_slider_moved(self, position):
        self.display_live_image()

    def grid_size_slider_pressed(self):
        self.display_live_image()


class RegistrationManualLauncher(object):

    parent = None

    def __init__(self, parent=None):
        self.parent = parent

        if self.parent.registration_tool_ui == None:
            tool_ui = RegistrationManual(parent=parent)
            tool_ui.show()
            self.parent.registration_tool_ui = tool_ui
        else:
            self.parent.registration_tool_ui.setFocus()
            self.parent.registration_tool_ui.activateWindow()


class RegistrationManual(QMainWindow):

    parent = None
    button_size = {'arrow': {'width': 100,
                             'height': 100},
                   'rotate': {'width': 100,
                              'height': 200},
                   'small_rotate': {'width': 50,
                                    'height': 100},
                   }

    list_arrow_widgets = []
    list_rotate_widgets = []

    def __init__(self, parent=None):
        self.parent = parent
        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindowTool()
        self.ui.setupUi(self)
        self.setWindowTitle("Registration Tool")
        self.initialize_widgets()
        self.update_status_widgets()

    def initialize_widgets(self):
        _file_path = os.path.dirname(__file__)
        up_arrow_file = os.path.abspath(os.path.join(_file_path, 'static/up_arrow.png'))
        self.ui.up_button.setIcon(QtGui.QIcon(up_arrow_file))

        down_arrow_file = os.path.abspath(os.path.join(_file_path, 'static/down_arrow.png'))
        self.ui.down_button.setIcon(QtGui.QIcon(down_arrow_file))

        right_arrow_file = os.path.abspath(os.path.join(_file_path, 'static/right_arrow.png'))
        self.ui.right_button.setIcon(QtGui.QIcon(right_arrow_file))

        left_arrow_file = os.path.abspath(os.path.join(_file_path, 'static/left_arrow.png'))
        self.ui.left_button.setIcon(QtGui.QIcon(left_arrow_file))

        rotate_left_file = os.path.abspath(os.path.join(_file_path, 'static/rotate_left.png'))
        self.ui.rotate_left_button.setIcon(QtGui.QIcon(rotate_left_file))

        rotate_right_file = os.path.abspath(os.path.join(_file_path, 'static/rotate_right.png'))
        self.ui.rotate_right_button.setIcon(QtGui.QIcon(rotate_right_file))

        small_rotate_left_file = os.path.abspath(os.path.join(_file_path, 'static/small_rotate_left.png'))
        self.ui.small_rotate_left_button.setIcon(QtGui.QIcon(small_rotate_left_file))

        small_rotate_right_file = os.path.abspath(os.path.join(_file_path, 'static/small_rotate_right.png'))
        self.ui.small_rotate_right_button.setIcon(QtGui.QIcon(small_rotate_right_file))

        self.list_arrow_widgets = [self.ui.up_button,
                              self.ui.down_button,
                              self.ui.left_button,
                              self.ui.right_button]
        self._set_widgets_size(widgets = self.list_arrow_widgets,
                              width = self.button_size['arrow']['width'],
                              height = self.button_size['arrow']['height'])

        self.list_rotate_widgets = [self.ui.rotate_left_button,
                                    self.ui.rotate_right_button]
        self._set_widgets_size(widgets = self.list_rotate_widgets,
                              width = self.button_size['rotate']['width'],
                              height = self.button_size['rotate']['height'])

        self.list_small_rotate_widgets = [self.ui.small_rotate_left_button,
                                        self.ui.small_rotate_right_button]
        self._set_widgets_size(widgets = self.list_small_rotate_widgets,
                              width = self.button_size['small_rotate']['width'],
                              height = self.button_size['small_rotate']['height'])


    def _set_widgets_size(self, widgets=[], width=10, height=10):
        for _widget in widgets:
            _widget.setIconSize(QtCore.QSize(width, height))

    def update_status_widgets(self):
            list_row_selected = self.parent.get_list_row_selected()
            _enabled = True

            if list_row_selected is None:
                _enabled = False

            elif not list_row_selected == []:
                if len(list_row_selected) == 1:
                    if list_row_selected[0] == self.parent.reference_image_index:
                        _enabled = False

            for _widget in self.list_arrow_widgets:
                _widget.setEnabled(_enabled)

            for _widget in self.list_rotate_widgets:
                _widget.setEnabled(_enabled)

            for _widget in self.list_small_rotate_widgets:
                _widget.setEnabled(_enabled)

    def closeEvent(self, c):
        self.parent.set_widget_status(list_ui=[self.parent.ui.auto_registration_button],
                           enabled=True)
        self.parent.registration_tool_ui = None

    def modified_selected_images(self, motion=None, rotation=0.):
        # retrieve row selected and changed values
        self.parent.ui.tableWidget.blockSignals(True)

        list_row_selected = self.parent.get_list_row_selected()
        for _row in list_row_selected:

            # we never modified the reference image
            if _row == self.parent.reference_image_index:
                continue

            if motion:

                # left and right - > we works with xoffset, column 1
                if motion in ['left', 'right']:
                    _old_value = np.int(self.parent.ui.tableWidget.item(_row, 1).text())

                    if motion == 'left':
                        xoffset = -1
                    else:
                        xoffset = 1

                    _new_value = _old_value + xoffset
                    self.parent.ui.tableWidget.item(_row, 1).setText(str(_new_value))

                else: # up and down -> yoffset, column 2

                    _old_value = np.int(self.parent.ui.tableWidget.item(_row, 2).text())

                    if motion == 'up':
                        yoffset = -1
                    else:
                        yoffset = 1

                    _new_value = _old_value + yoffset
                    self.parent.ui.tableWidget.item(_row, 2).setText(str(_new_value))

            if not rotation == 0: # column 3

                _old_value = np.float(self.parent.ui.tableWidget.item(_row, 3).text())
                _new_value = _old_value + rotation
                self.parent.ui.tableWidget.item(_row, 3).setText("{:.2f}".format(_new_value))

        self.parent.ui.tableWidget.blockSignals(False)
        self.parent.table_cell_modified(-1, -1)

    # event handler
    def left_button_clicked(self):
        self.modified_selected_images(motion='left')

    def right_button_clicked(self):
        self.modified_selected_images(motion='right')

    def up_button_clicked(self):
        self.modified_selected_images(motion='up')

    def down_button_clicked(self):
        self.modified_selected_images(motion='down')

    def small_rotate_left_button_clicked(self):
        self.modified_selected_images(rotation=.1)

    def small_rotate_right_button_clicked(self):
        self.modified_selected_images(rotation=-.1)

    def rotate_left_button_clicked(self):
        self.modified_selected_images(rotation=1)

    def rotate_right_button_clicked(self):
        self.modified_selected_images(rotation=-1)


class RegistrationFileSelection(object):

    def __init__(self, working_dir='./'):
        self.working_dir = working_dir

    def select_file_help(self, value):
        import webbrowser
        webbrowser.open("https://neutronimaging.pages.ornl.gov/en/tutorial/notebooks/file_selector/#select_profile")

    def load_files(self, files):
        o_norm = Normalization()
        o_norm.load(file=files, notebook=True)
        self.data_dict = o_norm.data

    def select_data(self):
        help_ui = widgets.Button(description="HELP",
                                 button_style='info')
        help_ui.on_click(self.select_file_help)
        display(help_ui)

        self.files_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select Images ...',
                                                             start_dir=self.working_dir,
                                                             next=self.load_files,
                                                             multiple=True)

        self.files_ui.show()

    def close(self):
        self.parent.registration_tool_ui = None


class RegistrationAutoConfirmationLauncher(object):

    parent = None

    def __init__(self, parent=None):
        self.parent=parent

        if self.parent.registration_auto_confirmation_ui == None:
            conf_ui = RegistrationManualAutoConfirmation(parent=parent)
            conf_ui.show()
            self.parent.registration_auto_confirmation_ui = conf_ui
        else:
            self.parent.registration_auto_confirmation_ui.setFocus()
            self.parent.registration_auto_confirmation_ui.activateWindow()


class RegistrationManualAutoConfirmation(QDialog):

    def __init__(self, parent=None):
        self.parent=parent
        QDialog.__init__(self, parent=None)
        self.ui = UiDialog()
        self.ui.setupUi(self)

        self.initialize_widgets()

    def initialize_widgets(self):
        _file_path = os.path.dirname(__file__)
        warning_image_file = os.path.abspath(os.path.join(_file_path, 'static/warning_icon.png'))
        warning_image = QtGui.QPixmap(warning_image_file)
        self.ui.warning_label.setPixmap(warning_image)

    def yes_button_clicked(self):
        self.parent.registration_auto_confirmation_ui.close()
        self.parent.registration_auto_confirmation_ui = None
        self.parent.start_auto_registration()

    def no_button_clicked(self):
        self.closeEvent()

    def closeEvent(self, event=None):
        self.parent.registration_auto_confirmation_ui.close()
        self.parent.registration_auto_confirmation_ui = None



class RegistrationAuto(object):

    registered_parameters = {}

    def __init__(self, parent=None, reference_image=[], floating_images=[]):
        self.parent = parent
        self.reference_image = reference_image
        self.list_images = floating_images

    def auto_align(self):
        _ref_image = self.reference_image
        _list_images = self.list_images

        nbr_images = len(_list_images)
        self.parent.eventProgress.setMaximum(nbr_images)
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)

        for _row,_image in enumerate(_list_images):
            [yoffset, xoffset], error, diffphase = register_translation(_ref_image,
                                                                        _image)
            if not _row == self.parent.reference_image_index:
                self.parent.set_item(row=_row, col=1, value=xoffset)
                self.parent.set_item(row=_row, col=2, value=yoffset)

            self.parent.eventProgress.setValue(_row+1)
            QtGui.QApplication.processEvents()

        self.parent.eventProgress.setVisible(False)

class ExportRegistration(object):

    def __init__(self, parent=None, export_folder=''):
        self.parent = parent
        self.export_folder = export_folder

    def run(self):
        data_dict_raw = copy.deepcopy(self.parent.data_dict_raw)
        list_file_names = data_dict_raw['file_name']
        nbr_files = len(data_dict_raw['data'])

        self.parent.eventProgress.setMaximum(nbr_files)
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)

        for _row, _data in enumerate(data_dict_raw['data']):
            _filename = list_file_names[_row]
            if not _row == self.parent.reference_image_index:

                _xoffset = np.int(self.parent.ui.tableWidget.item(_row, 1).text())
                _yoffset = np.int(self.parent.ui.tableWidget.item(_row, 2).text())
                _rotation = np.float(self.parent.ui.tableWidget.item(_row, 3).text())

                _data_registered = self.registered_data(raw_data=_data,
                                                        xoffset=_xoffset,
                                                        yoffset=_yoffset,
                                                        rotation=_rotation)
            else:

                _data_registered = _data

            o_norm = Normalization()
            o_norm.load(data=_data_registered)
            o_norm.data['sample']['metadata'] = [data_dict_raw['metadata'][_row]]
            o_norm.data['sample']['file_name'][0] = _filename
            # pprint.pprint(o_norm.data['sample'])
            # self.parent.testing_o_norm = o_norm
            o_norm.export(folder=self.export_folder, data_type='sample')

            self.parent.eventProgress.setValue(_row+1)
            QtGui.QApplication.processEvents()


        self.parent.eventProgress.setVisible(False)

    def registered_data(self, raw_data=[], xoffset=0, yoffset=0, rotation=0):

        _data = raw_data.copy()
        _data = transform.rotate(_data, rotation)
        _data = shift(_data, (yoffset, xoffset))

        return _data


class RegistrationMarkersLauncher(object):

    parent = None

    def __init__(self, parent=None):
        self.parent = parent

        if self.parent.registration_markers_ui == None:
            markers_ui = RegistrationMarkers(parent=parent)
            markers_ui.show()
            self.parent.registration_markers_ui = markers_ui
            self.parent.registration_markers_ui.init_widgets()
            #self.parent.display_markers(all=True)
        else:
            self.parent.registration_markers_ui.setFocus()
            self.parent.registration_markers_ui.activateWindow()


class RegistrationMarkers(QDialog):
    """dialog ui that will allow to add or remove markers
    This UI will also allow to change the color of the marker and to change
    their position linearly when selecting 2 of them (gradual increase between the 2)
    """

    def __init__(self, parent=None):
        self.parent = parent
        QDialog.__init__(self, parent=None)
        self.ui = UiDialogMarkers()
        self.ui.setupUi(self)

        self.nbr_files = len(self.parent.data_dict['file_name'])

    def resizing_column(self, index_column, old_size, new_size):
        """let's collect the size of the column in the current tab and then
        resize all the other columns of the other table"""

        _current_tab = self.ui.tabWidget.currentIndex()
        _tab_title = self.ui.tabWidget.tabText(_current_tab)

        _live_table_ui = self.parent.markers_table[_tab_title]['ui']
        nbr_column = _live_table_ui.columnCount()
        table_column_width = []
        for _col in np.arange(nbr_column):
            _width = _live_table_ui.columnWidth(_col)
            table_column_width.append(_width)

        self.parent.markers_table_column_width = table_column_width

        for _key in self.parent.markers_table.keys():
            _table_ui = self.parent.markers_table[_key]['ui']
            if not (_table_ui == _live_table_ui):
                for _col, _size in enumerate(self.parent.markers_table_column_width):
                    _table_ui.setColumnWidth(_col, self.parent.markers_table_column_width[_col])

    def init_widgets(self):
        if self.parent.markers_table == {}:
            self.add_marker_button_clicked()
        else:
            self.populate_using_markers_table()

    def update_markers_table_entry(self, marker_name='1', file=''):
        markers = self.parent.markers_table[marker_name]['data'][file]
        table_ui = self.parent.markers_table[marker_name]['ui']
        nbr_row = table_ui.rowCount()
        table_ui.blockSignals(True)

        x = str(markers['x'])
        y = str(markers['y'])

        for _row in np.arange(nbr_row):
            _file_name_of_row = str(table_ui.item(_row, 0).text())
            if _file_name_of_row == file:
                table_ui.item(_row, 1).setText(x)
                table_ui.item(_row, 2).setText(y)

        table_ui.blockSignals(False)

    def populate_using_markers_table(self):
        for _key_tab_name in self.parent.markers_table:

            _table = QtGui.QTableWidget(self.nbr_files, 3)
            _table.setHorizontalHeaderLabels(["File Name", "X", "Y"])
            _table.setAlternatingRowColors(True)

            for _col, _size in enumerate(self.parent.markers_table_column_width):
                _table.setColumnWidth(_col, self.parent.markers_table_column_width[_col])

            _table.horizontalHeader().sectionResized.connect(self.resizing_column)

            _data_dict = self.parent.markers_table[_key_tab_name]['data']
            for _row, _file in enumerate(self.parent.data_dict['file_name']):
                _short_file = os.path.basename(_file)
                x = _data_dict[_short_file]['x']
                y = _data_dict[_short_file]['y']
                self.__populate_table_row(_table, _row, _short_file, x, y)

            _table.itemChanged.connect(self.table_cell_modified)
            self.parent.markers_table[_key_tab_name]['ui'] = _table
            _ = self.ui.tabWidget.addTab(_table, _key_tab_name)
            self.parent.display_markers(all=False)

    def __populate_table_row(self, table_ui, row, file, x, y):
        # file name
        _item = QtGui.QTableWidgetItem(file)
        table_ui.setItem(row, 0, _item)
        _item.setFlags(QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsSelectable)

        # x
        _item = QtGui.QTableWidgetItem(str(x))
        table_ui.setItem(row, 1, _item)

        # y
        _item = QtGui.QTableWidgetItem(str(y))
        table_ui.setItem(row, 2, _item)

    def get_marker_name(self):
        markers_table = self.parent.markers_table
        keys = markers_table.keys()
        _marker_name = "1"
        if keys is None:
            return _marker_name

        while True:
            if _marker_name in markers_table:
                _marker_name = str(int(_marker_name)+1)
            else:
                return _marker_name

    def save_column_size(self):
        # using first table
        for _key in self.parent.markers_table.keys():
            _table_ui = self.parent.markers_table[_key]['ui']
            nbr_column = _table_ui.columnCount()
            table_column_width = []
            for _col in np.arange(nbr_column):
                _width = _table_ui.columnWidth(_col)
                table_column_width.append(_width)
            break
        self.parent.markers_table_column_width = table_column_width

    def save_current_table(self):
        _current_tab = self.ui.tabWidget.currentIndex()
        _tab_title = self.ui.tabWidget.tabText(_current_tab)

        # retrieve master markers dictionary
        markers_table = self.parent.markers_table
        # current table ui
        table_ui = markers_table[_tab_title]['ui']
        table_data = markers_table[_tab_title]['data']

        nbr_row = table_ui.rowCount()
        for _row in np.arange(nbr_row):
            file_name = str(table_ui.item(_row, 0).text())
            x = np.int(str(table_ui.item(_row, 1).text()))
            y = np.int(str(table_ui.item(_row, 2).text()))

            table_data[file_name]['x'] = x
            table_data[file_name]['y'] = y

        markers_table[_tab_title]['data'] = table_data
        self.parent.markers_table = markers_table

    # Event handler =================================

    def remove_marker_button_clicked(self):
        _current_tab = self.ui.tabWidget.currentIndex()
        _tab_title = self.ui.tabWidget.tabText(_current_tab)

        self.parent.markers_table.pop(_tab_title)
        self.ui.tabWidget.removeTab(_current_tab)
        self.parent.display_markers(all=True)

    def get_current_selected_color(self):
        color = self.ui.marker_color_widget.currentText()
        return (MarkerDefaultSettings.color[color], color)

    def add_marker_button_clicked(self):
        table = QtGui.QTableWidget(self.nbr_files, 3)
        table.setHorizontalHeaderLabels(["File Name", "X", "Y"])
        table.setAlternatingRowColors(True)
        for _col, _size in enumerate(self.parent.markers_table_column_width):
            table.setColumnWidth(_col, self.parent.markers_table_column_width[_col])

        table.horizontalHeader().sectionResized.connect(self.resizing_column)
        new_marker_name = self.get_marker_name()
        _ = self.ui.tabWidget.addTab(table, new_marker_name)

        _marker_dict = {}
        _marker_dict['ui'] = table

        (_qpen, _color_name) = self.get_current_selected_color()
        _marker_dict['color'] = {}
        _marker_dict['color']['qpen'] = _qpen
        _marker_dict['color']['name'] = _color_name

        _data_dict = {}
        for _row, _file in enumerate(self.parent.data_dict['file_name']):
            _short_file = os.path.basename(_file)
            x = self.parent.o_MarkerDefaultSettings.x
            y = self.parent.o_MarkerDefaultSettings.y
            self.__populate_table_row(table, _row, _short_file, x, y)
            _data_dict[_short_file] = {'x': x, 'y': y, 'marker_ui': None}

        _marker_dict['data'] = _data_dict

        # activate last index
        number_of_tabs = self.ui.tabWidget.count()
        self.ui.tabWidget.setCurrentIndex(number_of_tabs - 1)
        table.itemChanged.connect(self.table_cell_modified)
        self.parent.markers_table[new_marker_name] = _marker_dict
        self.parent.display_markers(all=False)

    def marker_color_changed(self, color):
        _current_tab = self.ui.tabWidget.currentIndex()
        _tab_title = self.ui.tabWidget.tabText(_current_tab)
        new_color = MarkerDefaultSettings.color[color]
        self.parent.markers_table[_tab_title]['color']['qpen'] = new_color
        self.parent.markers_table[_tab_title]['color']['name'] = color
        self.parent.display_markers_of_tab(marker_name=_tab_title)

    def table_cell_modified(self):
        self.save_current_table()
        self.parent.display_markers(all=False)

    def marker_tab_changed(self, tab_index):
        # first time, markers_table is still empty
        try:
            self.parent.markers_table[str(tab_index+1)]
            color = self.parent.markers_table[str(tab_index+1)]['color']['name']
            index_color = self.ui.marker_color_widget.findText(color)
            self.ui.marker_color_widget.setCurrentIndex(index_color)
            self.parent.display_markers()
        except KeyError:
            pass

    def closeEvent(self, c):
        self.save_column_size()
        self.parent.close_all_markers()
        self.parent.set_widget_status(list_ui=[self.parent.ui.auto_registration_button],
                           enabled=True)
        self.parent.registration_markers_ui = None


class MarkerDefaultSettings:

    x = 0
    y = 0

    width = 50
    height = 50
    
    color = {'white': pg.mkPen('w', width=2),
             'yellow': pg.mkPen('y', width=2),
             'green': pg.mkPen('g', width=2),
             'red': pg.mkPen('r', width=2),
             'blue': pg.mkPen('b', width=2),
             'cyan': pg.mkPen('c', width=2),
             'black': pg.mkPen('k', width=2),
             }

    def __init__(self, image_reference=[]):
        if not image_reference == []:
            [height, width] = np.shape(image_reference)
            self.x = np.int(width/2)
            self.y = np.int(height/2)



