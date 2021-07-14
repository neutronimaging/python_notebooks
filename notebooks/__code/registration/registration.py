from IPython.core.display import HTML
from IPython.core.display import display
from ipywidgets import widgets
import numpy as np
import os
from skimage import transform
from scipy.ndimage.interpolation import shift
from skimage.feature import register_translation
import copy
import pyqtgraph as pg
from pyqtgraph.dockarea import *
from qtpy.QtWidgets import QFileDialog, QDialog, QMainWindow
from qtpy import QtGui, QtCore

from NeuNorm.normalization import Normalization

from __code.ipywe import fileselector
from __code import load_ui
from __code.color import Color

from __code.ui_registration_auto_confirmation import Ui_Dialog as UiDialog
from __code.registration_profile import RegistrationProfileUi
from __code.registration.marker_default_settings import MarkerDefaultSettings
from __code.registration.registration_marker import RegistrationMarkersLauncher
from __code.registration.export_registration import ExportRegistration
from __code.registration.registration_auto import RegistrationAuto
from __code.registration.registration_auto_confirmation import RegistrationAutoConfirmationLauncher
from __code.registration.file_selection import FileSelection


class RegistrationUi(QMainWindow):

    table_registration = {} # dictionary that populate the table

    table_column_width = [650, 80, 80, 80]

    # image view
    histogram_level = []

    # by default, the reference image is the first image
    reference_image_index = 0
    reference_image = []
    reference_image_short_name = ''
    color_reference_background = QtGui.QColor(50, 250, 50)
    color_reference_profile = [50, 250, 50]

    nbr_files = 0

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
    registration_profile_ui = None

    # markers table
    # markers_table = {'1': {'data': {'file_0': {'x': 0, 'y':10, 'marker_ui': None, 'label_ui': None},
    #                                 'file_1': {'x': 0, 'y':10, 'marker_ui': None. 'label_ui': None},
    #                                 'file_2': {'x': 0, 'y':10, 'marker_ui': None, 'label_ui': None},
    #                                   ... },
    #                        'ui': None,
    #                        'color': {'qpen': None,
    #                                  'name': ""},
    #                 {'2': .... }
    markers_table = {}

    markers_table_column_width = [330, 50, 50]
    marker_table_buffer_cell = None

    def __init__(self, parent=None, data_dict=None):

        super(QMainWindow, self).__init__(parent)

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
            (maybe hidden behind this browser!)</span>'))
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_registration.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)

        # QMainWindow.__init__(self, parent=parent)
        # self.ui = UiMainWindow()
        # self.ui.setupUi(self)
        self.setWindowTitle("Registration")

        self.data_dict = data_dict # Normalization data dictionary  {'filename': [],
                                                                     #'data': [[...],[...]]],
                                                                     #'metadata': [],
                                                                     #'shape': {}}

        # untouched array of images (used to move and rotate images)
        self.data_dict_raw = copy.deepcopy(data_dict)
        self.reference_image = self.data_dict['data'][self.reference_image_index]
        self.working_dir = os.path.dirname(self.data_dict['file_name'][0])
        self.reference_image_short_name = str(os.path.basename(self.data_dict['file_name'][0]))

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
        self.nbr_files = nbr_files
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

        # update slide widget of files
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
        nbr_file_selected = len(list_short_file_selected)
        if nbr_file_selected > 1:
            list_row_selected = self.get_list_row_selected()
        _color_marker = self.markers_table[marker_name]['color']['name']

        pen = self.markers_table[marker_name]['color']['qpen']
        for _index, _file in enumerate(list_short_file_selected):
            _marker_data = self.markers_table[marker_name]['data'][_file]

            x = _marker_data['x']
            y = _marker_data['y']
            width = MarkerDefaultSettings.width
            height = MarkerDefaultSettings.height

            _marker_ui = pg.RectROI([x,y], [width, height], pen=pen)
            self.ui.image_view.addItem(_marker_ui)
            _marker_ui.removeHandle(0)
            _marker_ui.sigRegionChanged.connect(self.marker_has_been_moved)

            if nbr_file_selected > 1: # more than 1 file selected, we need to add the index of the file
                text_ui = self.add_marker_label(file_index=list_row_selected[_index],
                                                marker_index=marker_name,
                                                x=x,
                                                y=y,
                                                color=_color_marker)
                self.markers_table[marker_name]['data'][_file]['label_ui'] = text_ui

            _marker_data['marker_ui'] = _marker_ui

    def marker_has_been_moved(self):
        list_short_file_selected = self.get_list_short_file_selected()
        nbr_file_selected = len(list_short_file_selected)
        if nbr_file_selected > 1:
            list_row_selected = self.get_list_row_selected()

        for _index_marker, _marker_name in enumerate(self.markers_table.keys()):
            _color_marker = self.markers_table[_marker_name]['color']['name']
            for _index_file, _file in enumerate(list_short_file_selected):
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

                if nbr_file_selected > 1:
                    _label_ui = _marker_data['label_ui']
                    self.ui.image_view.removeItem(_label_ui)
                    _label_ui = self.add_marker_label(file_index = list_row_selected[_index_file],
                                                      marker_index = _index_marker,
                                                      x=x0,
                                                      y=y0,
                                                      color=_color_marker)
                    self.ui.image_view.addItem(_label_ui)
                    self.markers_table[_marker_name]['data'][_file]['label_ui'] = _label_ui

    def add_marker_label(self, file_index=0, marker_index=1, x=0, y=0, color='white'):
        html_color = MarkerDefaultSettings.color_html[color]
        html_text = '<div style="text-align: center">Marker#:'
        html_text += '<span style="color:#' + str(html_color) + ';">' + str(int(marker_index)+1)
        html_text += '</span> - File#:'
        html_text += '<span style="color:#' + str(html_color) + ';">' + str(file_index)
        html_text += '</span>'
        text_ui = pg.TextItem(html=html_text, angle=45, border='w')
        self.ui.image_view.addItem(text_ui)
        text_ui.setPos(x + MarkerDefaultSettings.width, y)
        return text_ui

    def close_markers_of_tab(self, marker_name=''):
        """remove box and label (if they are there) of each marker"""
        _data = self.markers_table[marker_name]['data']
        for _file in _data:
            _marker_ui = _data[_file]['marker_ui']
            if _marker_ui:
                self.ui.image_view.removeItem(_marker_ui)

            _label_ui = _data[_file]['label_ui']
            if _label_ui:
                self.ui.image_view.removeItem(_label_ui)

    def close_all_markers(self):
        for marker in self.markers_table.keys():
            self.close_markers_of_tab(marker_name = marker)


    def modified_images(self, list_row=[], all_row=False):
        """using data_dict_raw images, will apply offset and rotation parameters
        and will save them in data_dict for plotting"""

        data_raw = self.data_dict_raw['data'].copy()

        if all_row:
            list_row = np.arange(0, self.nbr_files)
        else:
            list_row =list_row

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

    def all_table_cell_modified(self):
        nbr_row = self.ui.tableWidget.rowCount()
        for _row in np.arange(nbr_row):
            self.modified_images(list_row=[_row])
            self.profile_line_moved()

    # Event handler

    def opacity_changed(self, opacity_value):
        self.display_image()

    def table_row_clicked(self, row=-1):
        self.ui.file_slider.blockSignals(True)
        if row == -1:
            row = self.ui.tableWidget.currentRow()
        else:
            self.ui.file_slider.setValue(row)

        self.display_image()
        self.check_selection_slider_status()
        self.profile_line_moved()
        self.check_selection_slider_status()
        self.check_status_next_prev_image_button()
        self.check_registration_tool_widgets()
        self.display_markers(all=True)
        self.ui.file_slider.blockSignals(False)

    def table_cell_modified(self, row=-1, column=-1):
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
        if self.registration_profile_ui:
            self.registration_profile_ui.close()

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

    def profiler_registration_button_clicked(self):
        o_registration_profile = RegistrationProfileLauncher(parent=self)

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


class RegistrationProfileLauncher(object):

    parent = None

    def __init__(self, parent=None):
        self.parent = parent

        if self.parent.registration_profile_ui == None:
            profile_ui = RegistrationProfileUi(parent=parent)
            profile_ui.show()
            self.parent.registration_profile_ui = profile_ui
        else:
            self.parent.registration_profile_ui.setFocus()
            self.parent.registration_profile_ui.activateWindow()


# class RegistrationManualLauncher(object):
#
#     parent = None
#
#     def __init__(self, parent=None):
#         self.parent = parent
#
#         if self.parent.registration_tool_ui == None:
#             tool_ui = RegistrationManual(parent=parent)
#             tool_ui.show()
#             self.parent.registration_tool_ui = tool_ui
#         else:
#             self.parent.registration_tool_ui.setFocus()
#             self.parent.registration_tool_ui.activateWindow()
#
#
# class RegistrationManual(QMainWindow):
#
#     parent = None
#     button_size = {'arrow': {'width': 100,
#                              'height': 100},
#                    'rotate': {'width': 100,
#                               'height': 200},
#                    'small_rotate': {'width': 50,
#                                     'height': 100},
#                    }
#
#     list_arrow_widgets = []
#     list_rotate_widgets = []
#
#     def __init__(self, parent=None):
#
#         super(QMainWindow, self).__init__(parent)
#
#         ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
#                                     os.path.join('ui',
#                                                  'ui_registration_tool.ui'))
#         self.ui = load_ui(ui_full_path, baseinstance=self)
#         self.parent = parent
#         self.setWindowTitle("Registration Tool")
#         self.initialize_widgets()
#         self.update_status_widgets()
#
#     def initialize_widgets(self):
#         _file_path = os.path.dirname(__file__)
#         up_arrow_file = os.path.abspath(os.path.join(_file_path, '../static/up_arrow.png'))
#         self.ui.up_button.setIcon(QtGui.QIcon(up_arrow_file))
#
#         down_arrow_file = os.path.abspath(os.path.join(_file_path, '../static/down_arrow.png'))
#         self.ui.down_button.setIcon(QtGui.QIcon(down_arrow_file))
#
#         right_arrow_file = os.path.abspath(os.path.join(_file_path, '../static/right_arrow.png'))
#         self.ui.right_button.setIcon(QtGui.QIcon(right_arrow_file))
#
#         left_arrow_file = os.path.abspath(os.path.join(_file_path, '../static/left_arrow.png'))
#         self.ui.left_button.setIcon(QtGui.QIcon(left_arrow_file))
#
#         rotate_left_file = os.path.abspath(os.path.join(_file_path, '../static/rotate_left.png'))
#         self.ui.rotate_left_button.setIcon(QtGui.QIcon(rotate_left_file))
#
#         rotate_right_file = os.path.abspath(os.path.join(_file_path, '../static/rotate_right.png'))
#         self.ui.rotate_right_button.setIcon(QtGui.QIcon(rotate_right_file))
#
#         small_rotate_left_file = os.path.abspath(os.path.join(_file_path, '../static/small_rotate_left.png'))
#         self.ui.small_rotate_left_button.setIcon(QtGui.QIcon(small_rotate_left_file))
#
#         small_rotate_right_file = os.path.abspath(os.path.join(_file_path, '../static/small_rotate_right.png'))
#         self.ui.small_rotate_right_button.setIcon(QtGui.QIcon(small_rotate_right_file))
#
#         self.list_arrow_widgets = [self.ui.up_button,
#                               self.ui.down_button,
#                               self.ui.left_button,
#                               self.ui.right_button]
#         self._set_widgets_size(widgets = self.list_arrow_widgets,
#                               width = self.button_size['arrow']['width'],
#                               height = self.button_size['arrow']['height'])
#
#         self.list_rotate_widgets = [self.ui.rotate_left_button,
#                                     self.ui.rotate_right_button]
#         self._set_widgets_size(widgets = self.list_rotate_widgets,
#                               width = self.button_size['rotate']['width'],
#                               height = self.button_size['rotate']['height'])
#
#         self.list_small_rotate_widgets = [self.ui.small_rotate_left_button,
#                                         self.ui.small_rotate_right_button]
#         self._set_widgets_size(widgets = self.list_small_rotate_widgets,
#                               width = self.button_size['small_rotate']['width'],
#                               height = self.button_size['small_rotate']['height'])
#
#
#     def _set_widgets_size(self, widgets=[], width=10, height=10):
#         for _widget in widgets:
#             _widget.setIconSize(QtCore.QSize(width, height))
#
#     def update_status_widgets(self):
#             list_row_selected = self.parent.get_list_row_selected()
#             _enabled = True
#
#             if list_row_selected is None:
#                 _enabled = False
#
#             elif not list_row_selected == []:
#                 if len(list_row_selected) == 1:
#                     if list_row_selected[0] == self.parent.reference_image_index:
#                         _enabled = False
#
#             for _widget in self.list_arrow_widgets:
#                 _widget.setEnabled(_enabled)
#
#             for _widget in self.list_rotate_widgets:
#                 _widget.setEnabled(_enabled)
#
#             for _widget in self.list_small_rotate_widgets:
#                 _widget.setEnabled(_enabled)
#
#     def closeEvent(self, c):
#         self.parent.set_widget_status(list_ui=[self.parent.ui.auto_registration_button],
#                            enabled=True)
#         self.parent.registration_tool_ui = None
#
#     def modified_selected_images(self, motion=None, rotation=0.):
#         # retrieve row selected and changed values
#         self.parent.ui.tableWidget.blockSignals(True)
#
#         list_row_selected = self.parent.get_list_row_selected()
#         for _row in list_row_selected:
#
#             # we never modified the reference image
#             if _row == self.parent.reference_image_index:
#                 continue
#
#             if motion:
#
#                 # left and right - > we works with xoffset, column 1
#                 if motion in ['left', 'right']:
#                     _old_value = np.int(self.parent.ui.tableWidget.item(_row, 1).text())
#
#                     if motion == 'left':
#                         xoffset = -1
#                     else:
#                         xoffset = 1
#
#                     _new_value = _old_value + xoffset
#                     self.parent.ui.tableWidget.item(_row, 1).setText(str(_new_value))
#
#                 else: # up and down -> yoffset, column 2
#
#                     _old_value = np.int(self.parent.ui.tableWidget.item(_row, 2).text())
#
#                     if motion == 'up':
#                         yoffset = -1
#                     else:
#                         yoffset = 1
#
#                     _new_value = _old_value + yoffset
#                     self.parent.ui.tableWidget.item(_row, 2).setText(str(_new_value))
#
#             if not rotation == 0: # column 3
#
#                 _old_value = np.float(self.parent.ui.tableWidget.item(_row, 3).text())
#                 _new_value = _old_value + rotation
#                 self.parent.ui.tableWidget.item(_row, 3).setText("{:.2f}".format(_new_value))
#
#         self.parent.ui.tableWidget.blockSignals(False)
#         self.parent.table_cell_modified(-1, -1)
#
#     # event handler
#     def left_button_clicked(self):
#         self.modified_selected_images(motion='left')
#
#     def right_button_clicked(self):
#         self.modified_selected_images(motion='right')
#
#     def up_button_clicked(self):
#         self.modified_selected_images(motion='up')
#
#     def down_button_clicked(self):
#         self.modified_selected_images(motion='down')
#
#     def small_rotate_left_button_clicked(self):
#         self.modified_selected_images(rotation=.1)
#
#     def small_rotate_right_button_clicked(self):
#         self.modified_selected_images(rotation=-.1)
#
#     def rotate_left_button_clicked(self):
#         self.modified_selected_images(rotation=1)
#
#     def rotate_right_button_clicked(self):
#         self.modified_selected_images(rotation=-1)
