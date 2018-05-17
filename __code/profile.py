from IPython.core.display import HTML
from IPython.core.display import display

import numpy as np
import os
import copy
import pyqtgraph as pg
from skimage import transform

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
from __code.ui_profile import Ui_MainWindow as UiMainWindow
from __code.decorators import wait_cursor


class ProfileUi(QMainWindow):

    data_dict = {}
    data_dict_raw = {}
    timestamp_dict = {}

    rotation_angle = 0
    histogram_level = []

    # size of tables
    _width = 65
    guide_table_width = [80, _width, _width, _width, _width]
    guide_table_height = 50
    summary_table_width = [300, 150, 100]

    live_image = []
    grid_view = {'pos': None,
                 'adj': None,
                 'item': None,
                 'color': (0, 0, 255, 255, 1)}

    profile_color = (0, 255, 0, 255, 1)

    display_ui = []

    # guide and profile pg ROIs
    list_guide_pyqt_roi = list()
    list_profile_pyqt_roi = list()
    list_table_widget_checkbox = list()
    default_guide_roi = {'x0': 0, 'y0': 0, 'width':200, 'height': 800,
                         'isChecked': True,
                         'color_activated':'r',
                         'color_deactivated': 'b'}
    previous_active_row = -1 # use to deactivated the guide and profile roi

    # default_guide_table_values = {'isChecked': True, 'x0': 0, 'y0': 0,
    #                               'width': 200, 'height': 200}
    default_profile_width_values = np.arange(1,50,2)


    #remove-me
    test_roi = None

    def __init__(self, parent=None, working_dir='', data_dict=None):

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
            (maybe hidden behind this browser!)</span>'))

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Profile")

        self.working_dir = working_dir
        self.data_dict = data_dict # Normalization data dictionary  {'file_name': [],
                                                                     #'data': [[...],[...]]],
                                                                     #'metadata': [],
                                                                     #'shape': {}}

        # untouched array of images (used to move and rotate images)
        self.data_dict_raw = copy.deepcopy(data_dict)

        # initialization
        o_initialization = Initializer(parent=self)
        o_initialization.timestamp_dict()
        o_initialization.table()
        o_initialization.parameters()
        o_initialization.widgets()
        o_initialization.pyqtgraph()

        # display first images
        self.slider_file_changed(-1)

    # main methods
    def remove_all_guides(self):
        # remove all teh guids
        for _roi in self.list_guide_pyqt_roi:
            self.ui.image_view.removeItem(_roi)

    def display_guides(self):
        # check if we want to display this guide or not
        nbr_row = self.ui.tableWidget.rowCount()
        for row in np.arange(nbr_row):
            _guide = self.list_guide_pyqt_roi[row]
            _widget = self.ui.tableWidget.cellWidget(row, 0).children()[1]
            if _widget.isChecked():
                self.ui.image_view.addItem(_guide)

    def remove_all_profiles(self):
        for _roi in self.list_profile_pyqt_roi:
            self.ui.image_view.removeItem(_roi)

    def display_profiles(self):
        nbr_row = self.ui.tableWidget.rowCount()
        if nbr_row == 0:
            return

        image = self.live_image
        color = Color()
        list_rgb_profile_color = color.get_list_rgb(nbr_color=nbr_row)

        self.ui.profile_view.clear()
        try:
            self.ui.profile_view.scene().removeItem(self.legend)
        except Exception as e:
            print(e)

        self.legend = self.ui.profile_view.addLegend()

        for _row in np.arange(nbr_row):
            [x_axis, profile] = self.get_profile(image=image, profile_roi_row=_row)
            _label = ' Profile #{}'.format(_row+1)
            _color = list_rgb_profile_color[_row]
            self.ui.profile_view.plot(x_axis, profile,
                                        name=_label,
                                        pen=_color)

    def display_image(self, recalculate_image=False):
        """display the image selected by the file slider"""
        o_image = DisplayImages(parent=self, recalculate_image=recalculate_image)

    def remove_row(self, row=-1):

        if row == -1:
            return

        self.ui.tableWidget.removeRow(row)
        self.ui.tableWidget_2.removeRow(row)
        self.ui.image_view.removeItem(self.list_guide_pyqt_roi[row])
        self.list_guide_pyqt_roi.remove(self.list_guide_pyqt_roi[row])
        self.ui.image_view.removeItem(self.list_profile_pyqt_roi[row])
        self.list_profile_pyqt_roi.remove(self.list_profile_pyqt_roi[row])
        # self.list_table_widget_checkbox.remove(self.list_profile_pyqt_roi[row])

        nbr_row = self.ui.tableWidget.rowCount()
        if row == nbr_row:
            row -= 1

        if nbr_row > 0:
            nbr_col = self.ui.tableWidget.columnCount()
            new_selection = QtGui.QTableWidgetSelectionRange(row, 0, row, nbr_col - 1)
            self.ui.tableWidget.setRangeSelected(new_selection, True)
            new_selection_2 = QtGui.QTableWidgetSelectionRange(row, 0, row, 1)
            self.ui.tableWidget_2.setRangeSelected(new_selection_2, True)

    def update_guide_roi_using_guide_table(self, row=-1):
        [x0, y0, width, height] = self.get_item_row(row=row)
        roi_ui = self.list_guide_pyqt_roi[row]
        roi_ui.blockSignals(True)
        roi_ui.setPos((x0, y0))
        roi_ui.setSize((width, height))
        roi_ui.blockSignals(False)

    def update_profile_rois(self, row=-1):
        if row == -1: # update all of them

            # # remove all profile rois
            # self.list_profile_pyqt_roi = list()
            # for _profile_roi in self.list_profile_pyqt_roi:
            #     self.ui.image_view.removeItem(_profile_roi)

            nbr_row = self.ui.tableWidget.rowCount()
            for _row in np.arange(nbr_row):
                self.update_profile_rois(row=_row)

        else:
            self.update_profile_pyqt_roi(row=row)

    def is_row_enabled(self, row=-1):
        """check if the first column (enabled widget) is checked"""
        if row == -1:
            return None
        _widget = self.ui.tableWidget.cellWidget(row, 0).children()[1]
        if _widget.isChecked():
            return True
        return false

    def update_guide_table_using_guide_rois(self):
        for _row, _roi in enumerate(self.list_guide_pyqt_roi):
            if self.is_row_enabled(row=_row):
                region = _roi.getArraySlice(self.live_image,
                                            self.ui.image_view.imageItem)

                x0 = region[0][0].start
                x1 = region[0][0].stop
                y0 = region[0][1].start
                y1 = region[0][1].stop

                width = np.abs(x1 - x0)-1
                height = np.abs(y1 - y0)-1

                self.set_item_main_table(row=_row, col=1, value=str(x0))
                self.set_item_main_table(row=_row, col=2, value=str(y0))
                self.set_item_main_table(row=_row, col=3, value=str(width))
                self.set_item_main_table(row=_row, col=4, value=str(height))

    def add_guide_and_profile_pyqt_roi(self, row=-1):
        """add the pyqtgraph roi guide and profiles"""
        o_profile = GuideAndProfileRoisHandler(parent=self, row=row)
        o_profile.add()

    def update_profile_pyqt_roi(self, row=-1):
        o_profile = GuideAndProfileRoisHandler(parent=self, row=row)
        o_profile.update()

    def insert_row(self, row=-1):
        if row == -1:
            row = 0

        self.ui.tableWidget.blockSignals(True)
        default_values = self.default_guide_roi

        self.ui.tableWidget.insertRow(row)
        self.ui.tableWidget.setRowHeight(row, self.guide_table_height)

        self.set_item_main_table(row=row, col=0, value=default_values['isChecked'])
        self.set_item_main_table(row=row, col=1, value=default_values['x0'])
        self.set_item_main_table(row=row, col=2, value=default_values['y0'])
        self.set_item_main_table(row=row, col=3, value=default_values['width'])
        self.set_item_main_table(row=row, col=4, value=default_values['height'])

        # select new entry
        nbr_row = self.ui.tableWidget.rowCount()
        nbr_col = self.ui.tableWidget.columnCount()
        full_range = QtGui.QTableWidgetSelectionRange(0, 0, nbr_row - 1, nbr_col - 1)
        self.ui.tableWidget.setRangeSelected(full_range, False)
        new_selection = QtGui.QTableWidgetSelectionRange(row, 0, row, nbr_col - 1)
        self.ui.tableWidget.setRangeSelected(new_selection, True)
        self.ui.tableWidget.blockSignals(False)

        self.ui.tableWidget_2.blockSignals(True)
        self.ui.tableWidget_2.insertRow(row)
        self.ui.tableWidget_2.setRowHeight(row, self.guide_table_height)
        self.set_item_profile_table(row=row)

        # select new entry
        nbr_col = self.ui.tableWidget_2.columnCount()
        full_range = QtGui.QTableWidgetSelectionRange(0, 0, nbr_row - 1, nbr_col - 1)
        self.ui.tableWidget_2.setRangeSelected(full_range, False)
        new_selection = QtGui.QTableWidgetSelectionRange(row, 0, row, nbr_col - 1)
        self.ui.tableWidget_2.setRangeSelected(new_selection, True)
        self.ui.tableWidget_2.blockSignals(False)

    # setter
    def set_item_profile_table(self, row=0):
        spacerItem_left = QtGui.QSpacerItem(408, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        widget = QtGui.QComboBox()
        widget.addItems(self.default_profile_width_values)
        widget.blockSignals(True)
        widget.currentIndexChanged.connect(self.profile_width_changed)
        spacerItem_right = QtGui.QSpacerItem(408, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        hori_layout = QtGui.QHBoxLayout()
        hori_layout.addItem(spacerItem_left)
        hori_layout.addWidget(widget)
        hori_layout.addItem(spacerItem_right)
        cell_widget = QtGui.QWidget()
        cell_widget.setLayout(hori_layout)
        self.ui.tableWidget_2.setCellWidget(row, 0, cell_widget)
        widget.blockSignals(False)

    def set_item_main_table(self, row=0, col=0, value=''):
        if col == 0:
            spacerItem_left = QtGui.QSpacerItem(408, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
            widget = QtGui.QCheckBox()
            widget.blockSignals(True)
            self.list_table_widget_checkbox.insert(row, widget)
            widget.stateChanged.connect(self.guide_state_changed)
            spacerItem_right = QtGui.QSpacerItem(408, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
            hori_layout = QtGui.QHBoxLayout()
            hori_layout.addItem(spacerItem_left)
            hori_layout.addWidget(widget)
            hori_layout.addItem(spacerItem_right)
            cell_widget = QtGui.QWidget()
            cell_widget.setLayout(hori_layout)
            if value is True:
                widget.setCheckState(QtCore.Qt.Checked)
            else:
                widget.setCheckState(QtCore.Qt.Unchecked)
            self.ui.tableWidget.setCellWidget(row, col, cell_widget)
            widget.blockSignals(False)
        else:
            item = QtGui.QTableWidgetItem(str(value))
            self.ui.tableWidget.setItem(row, col, item)

    def get_profile(self, image=[], profile_roi_row=-1):
        is_x_profile_direction = self.ui.profile_direction_x_axis.isChecked()
        [x0, y0, width, height] = self.get_item_row(row=profile_roi_row)
        delta_profile = self.get_profile_width(row=profile_roi_row)

        if is_x_profile_direction:
            x_left = x0
            x_right = x0 + width

            profile_center = y0 + np.abs(np.int((height)/2.))
            y_top = profile_center - delta_profile
            y_bottom = profile_center + delta_profile

            mean_axis = 1
            x_axis = np.arange(x_left, x_right)

        else:
            profile_center = x0 + np.abs(np.int((width) / 2.))
            x_left = profile_center - delta_profile
            x_right = profile_center + delta_profile

            y_top = y0
            y_bottom = y0 + height

            mean_axis = 0
            x_axis = np.arange(y_top, y_bottom)

        _data = image[x_left: x_right, y_top:y_bottom]  # because pyqtgrpah display transpose images
        profile = np.mean(_data, axis=mean_axis)
        return [x_axis, profile]

    def get_profile_width(self, row=0):
        _widget = self.ui.tableWidget_2.cellWidget(row, 0).children()[1]
        return np.int(str(_widget.currentText()))

    def get_item_row(self, row=0):
        x0 = np.int(str(self.ui.tableWidget.item(row, 1).text()))
        y0 = np.int(str(self.ui.tableWidget.item(row, 2).text()))
        width = np.int(str(self.ui.tableWidget.item(row, 3).text()))
        height = np.int(str(self.ui.tableWidget.item(row, 4).text()))
        return (x0, y0, width, height)

    def get_selected_row(self, source='tableWidget'):
        if source == 'tableWidget':
            ui = self.ui.tableWidget
        else:
            ui = self.ui.tableWidget_2
        selection = ui.selectedRanges()
        if selection:
            top_row = selection[0].topRow()
            return top_row
        else:
            return -1

    def _highlights_guide_profile_pyqt_roi(self, row=-1, status='activated'):
        if row == -1:
            return
        _guide_ui = self.list_guide_pyqt_roi[row]
        _guide_ui.setPen(self.default_guide_roi['color_' + status])

    def highlight_guide_profile_pyqt_rois(self, row=-1):
        """When user click a row in the table, the correspoinding ROI will be activated and ots
        color will change. The old activated guide and profile will then be deactivated and color will
        change as well according to the color definition found in the self.default_guide_roi dictionary"""
        previous_active_row = self.previous_active_row
        if previous_active_row == -1:
            return

        self._highlights_guide_profile_pyqt_roi(row=previous_active_row, status='deactivated')
        self._highlights_guide_profile_pyqt_roi(row=row, status='activated')

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
        self.ui.file_slider.setValue(new_row_selected)
        self.check_status_next_prev_image_button()
        self.display_image()
        self.ui.file_slider.blockSignals(False)
        self.display_profiles()

    def slider_file_changed(self, index_selected):
        self.display_image()
        slider_value = self.ui.file_slider.value()
        self.ui.image_slider_value.setText(str(slider_value))
        self.check_status_next_prev_image_button()
        self.display_profiles()

    ## Event Handler
    def tab_changed(self, tab_index):
        pass
        # if tab_index == 1: # update table
        #     self.update_summary_table()

    def guide_changed(self):
        self.update_guide_table_using_guide_rois()
        self.update_profile_rois()

    def table_widget_selection_changed(self):
        self.ui.tableWidget_2.blockSignals(True)
        nbr_col = self.ui.tableWidget_2.columnCount()
        nbr_row = self.ui.tableWidget_2.rowCount()
        full_range = QtGui.QTableWidgetSelectionRange(0, 0, nbr_row - 1, nbr_col - 1)
        self.ui.tableWidget_2.setRangeSelected(full_range, False)
        row = self.get_selected_row()
        new_selection = QtGui.QTableWidgetSelectionRange(row, 0, row, nbr_col - 1)
        self.ui.tableWidget_2.setRangeSelected(new_selection, True)
        self.highlight_guide_profile_pyqt_rois(row=row)
        self.ui.tableWidget_2.blockSignals(False)
        self.previous_active_row = row

    def table_widget_2_selection_changed(self):
        self.ui.tableWidget.blockSignals(True)
        nbr_col = self.ui.tableWidget.columnCount()
        nbr_row = self.ui.tableWidget.rowCount()
        full_range = QtGui.QTableWidgetSelectionRange(0, 0, nbr_row - 1, nbr_col - 1)
        self.ui.tableWidget.setRangeSelected(full_range, False)
        row = self.get_selected_row(source='tableWidget_2')
        new_selection = QtGui.QTableWidgetSelectionRange(row, 0, row, nbr_col - 1)
        self.ui.tableWidget.setRangeSelected(new_selection, True)
        self.highlight_guide_profile_pyqt_rois(row=row)
        self.ui.tableWidget.blockSignals(False)
        self.previous_active_row = row

    def table_widget_cell_changed(self, row, column):
        self.update_guide_roi_using_guide_table(row=row)
        self.update_profile_rois(row=row)
        self.display_profiles()

    def guide_state_changed(self, state):
        self.remove_all_guides()
        self.display_guides()
        self.display_profiles()

    def profile_width_changed(self, new_value):
        self.update_profile_rois()
        self.display_profiles()

    def display_grid_clicked(self):
        status = self.ui.grid_display_checkBox.isChecked()
        for _widget in self.display_ui:
            _widget.setEnabled(status)
        self.display_image()

    def grid_size_slider_clicked(self):
        self.display_image()

    def grid_size_slider_released(self):
        self.display_image()

    def grid_size_slider_moved(self, value):
        self.display_image()

    def transparency_slider_clicked(self):
        self.display_image()

    def transparency_slider_moved(self, value):
        self.display_image()

    @wait_cursor
    def right_rotation_slow_clicked(self):
        self.rotation_angle -= 0.1
        self.display_image(recalculate_image=True)
        self.display_profiles()

    @wait_cursor
    def left_rotation_slow_clicked(self):
        self.rotation_angle += 0.1
        self.display_image(recalculate_image=True)
        self.display_profiles()

    @wait_cursor
    def right_rotation_fast_clicked(self):
        self.rotation_angle -= 1
        self.display_image(recalculate_image=True)
        self.display_profiles()

    @wait_cursor
    def left_rotation_fast_clicked(self):
        self.rotation_angle += 1
        self.display_image(recalculate_image=True)
        self.display_profiles()

    def add_row_button_clicked(self):
        selected_row = self.get_selected_row()
        self._highlights_guide_profile_pyqt_roi(row=selected_row, status='deactivated')
        self.insert_row(row=selected_row)
        self.add_guide_and_profile_pyqt_roi(row=selected_row)
        self.previous_active_row = selected_row
        self.display_profiles()

    def remove_row_button_clicked(self):
        selected_row = self.get_selected_row()
        self.remove_row(row=selected_row)
        self.display_profiles()

    def profile_along_axis_changed(self):
        self.update_profile_rois()
        self.display_profiles()

    def export_button_clicked(self):
        print("export button clicked")
        # _export_folder = QFileDialog.getExistingDirectory(self,
        #                                                   directory=self.working_dir,
        #                                                   caption = "Select Output Folder",
        #                                                   options=QFileDialog.ShowDirsOnly)
        # if _export_folder:
        #     o_export = ExportCalibration(parent = self,
        #                                  export_folder = _export_folder)
        #     o_export.run()
        #     QtGui.QGuiApplication.processEvents()

    def previous_image_button_clicked(self):
        self.change_slider(offset = -1)
        # self.display_measurement_profiles()

    def next_image_button_clicked(self):
        self.change_slider(offset = +1)
        # self.display_measurement_profiles()

    def help_button_clicked(self):
        import webbrowser
        webbrowser.open("https://neutronimaging.pages.ornl.gov/en/tutorial/notebooks/profile/")

    def closeEvent(self, event=None):
        pass


    
class GuideAndProfileRoisHandler(object):

    __profile = None

    def __init__(self, parent=None, row=-1):
        self.parent = parent
        self.row = row
        if self.row == -1:
            self.row = 0

    def add(self):
        self._define_guide()
        self._define_profile()
        self.parent.list_profile_pyqt_roi.insert(self.row, self.__profile)

    def update(self):
        self._define_profile()
        self.parent.ui.image_view.removeItem(self.parent.list_profile_pyqt_roi[self.row])
        self.parent.list_profile_pyqt_roi[self.row] = self.__profile

    def _define_guide(self):
        """define the guide"""
        guide_roi = pg.RectROI([self.parent.default_guide_roi['x0'], self.parent.default_guide_roi['y0']],
                                [self.parent.default_guide_roi['width'], self.parent.default_guide_roi['height']],
                            pen=self.parent.default_guide_roi['color_activated'])
        guide_roi.addScaleHandle([1, 1], [0, 0])
        guide_roi.addScaleHandle([0, 0], [1, 1])
        guide_roi.sigRegionChanged.connect(self.parent.guide_changed)
        self.parent.ui.image_view.addItem(guide_roi)
        self.parent.list_guide_pyqt_roi.insert(self.row, guide_roi)

    def _define_profile(self):
        # profile
        [x0, y0, width, height] = self.parent.get_item_row(row=self.row)
        _profile_width = self.parent.get_profile_width(row=self.row)
        is_x_profile_direction = self.parent.ui.profile_direction_x_axis.isChecked()
        delta_profile = (_profile_width - 1) / 2.
        if is_x_profile_direction:

            profile_center = y0 + np.abs(np.int((height)/2.))

            y_top = profile_center - delta_profile
            y_bottom = profile_center + delta_profile

            x_left = x0
            x_right = x0 + width

            pos = []
            pos.append([x_left, y_top])
            pos.append([x_right, y_top])
            adj = []
            adj.append([0, 1])

            if y_top != y_bottom: # height == 1
                pos.append([x_left, y_bottom])
                pos.append([x_right, y_bottom])
                adj.append([2, 3])

            adj = np.array(adj)
            pos = np.array(pos)

        else: # y-profile direction

            profile_center = x0 + np.abs(np.int((width) / 2.))

            x_left = profile_center - delta_profile
            x_right = profile_center + delta_profile

            y_top = y0
            y_bottom = y0 + height

            pos = []
            pos.append([x_left, y_top])
            pos.append([x_left, y_bottom])
            adj = []
            adj.append([0, 1])

            if y_top != y_bottom:  # height == 1
                pos.append([x_right, y_top])
                pos.append([x_right, y_bottom])
                adj.append([2, 3])

            adj = np.array(adj)
            pos = np.array(pos)

        line_color = self.parent.profile_color
        _list_line_color = list(line_color)
        line_color = tuple(_list_line_color)
        lines = np.array([line_color for n in np.arange(len(pos))],
                         dtype=[('red', np.ubyte), ('green', np.ubyte),
                                ('blue', np.ubyte), ('alpha', np.ubyte),
                                ('width', float)])

        profile = pg.GraphItem()
        self.parent.ui.image_view.addItem(profile)
        profile.setData(pos=pos,
                     adj=adj,
                     pen=lines,
                     symbol=None,
                     pxMode=False)

        self.__profile = profile


class Initializer(object):

    def __init__(self, parent=None):
        self.parent = parent

    def timestamp_dict(self):
        list_files = self.parent.data_dict['file_name']
        self.parent.timestamp_dict = retrieve_time_stamp(list_files)

    def table(self):
        # init the summary table
        list_files_full_name = self.parent.data_dict['file_name']
        list_files_short_name = [os.path.basename(_file) for _file in list_files_full_name]

        list_time_stamp = self.parent.timestamp_dict['list_time_stamp']
        list_time_stamp_user_format = self.parent.timestamp_dict['list_time_stamp_user_format']
        time_0 = list_time_stamp[0]
        for _row, _file in enumerate(list_files_short_name):
            self.parent.ui.summary_table.insertRow(_row)
            self.set_item_summary_table(row=_row, col=0, value=_file)
            self.set_item_summary_table(row=_row, col=1, value=list_time_stamp_user_format[_row])
            _offset = list_time_stamp[_row] - time_0
            self.set_item_summary_table(row=_row, col=2, value="{:0.2f}".format(_offset))
    
    def parameters(self):        
        # init the position of the measurement ROI
        [height, width] = np.shape(self.parent.data_dict['data'][0])
        self.parent.default_guide_roi['width'] = np.int(width/10)
        self.parent.default_guide_roi['height'] = np.int(height/5)
        self.parent.default_guide_roi['x0'] = np.int(width/2)
        self.parent.default_guide_roi['y0'] = np.int(height/2)
        self.parent.default_profile_width_values = [str(_value) for _value in self.parent.default_profile_width_values]

    def widgets(self):
        _file_path = os.path.dirname(__file__)
        left_rotation_fast_file = os.path.abspath(os.path.join(_file_path,
                                                               'static/profile/button_rotation_left_fast.png'))
        self.parent.ui.left_rotation_button_fast.setStyleSheet("background-image: "
                                                        "url('" + left_rotation_fast_file + "'); " + \
                                                        "background-repeat: no-repeat")

        right_rotation_fast_file = os.path.abspath(os.path.join(_file_path,
                                                                'static/profile/button_rotation_right_fast.png'))
        self.parent.ui.right_rotation_button_fast.setStyleSheet("background-image: "
                                                         "url('" + right_rotation_fast_file + "'); " + \
                                                         "background-repeat: no-repeat")

        left_rotation_slow_file = os.path.abspath(os.path.join(_file_path,
                                                               'static/profile/button_rotation_left_slow.png'))
        self.parent.ui.left_rotation_button_slow.setStyleSheet("background-image: "
                                                        "url('" + left_rotation_slow_file + "'); " + \
                                                        "background-repeat: no-repeat")

        right_rotation_slow_file = os.path.abspath(os.path.join(_file_path,
                                                                'static/profile/button_rotation_right_slow.png'))
        self.parent.ui.right_rotation_button_slow.setStyleSheet("background-image: "
                                                         "url('" + right_rotation_slow_file + "'); " + \
                                                         "background-repeat: no-repeat")

        self.parent.ui.splitter_2.setSizes([250, 50])
        self.parent.ui.splitter.setSizes([500, 50])

        # file slider
        self.parent.ui.file_slider.setMaximum(len(self.parent.data_dict['data']) - 1)

        # update size of table columns
        nbr_columns = self.parent.ui.tableWidget.columnCount()
        for _col in range(nbr_columns):
            self.parent.ui.tableWidget.setColumnWidth(_col, self.parent.guide_table_width[_col])

        # update size of summary table
        nbr_columns = self.parent.ui.summary_table.columnCount()
        for _col in range(nbr_columns):
            self.parent.ui.summary_table.setColumnWidth(_col, self.parent.summary_table_width[_col])

        self.parent.display_ui = [self.parent.ui.display_size_label,
                           self.parent.ui.grid_size_slider,
                           self.parent.ui.display_transparency_label,
                           self.parent.ui.transparency_slider]

    def pyqtgraph(self):
        # image
        self.parent.ui.image_view = pg.ImageView(view=pg.PlotItem())
        self.parent.ui.image_view.ui.menuBtn.hide()
        self.parent.ui.image_view.ui.roiBtn.hide()
        vertical_layout = QtGui.QVBoxLayout()
        vertical_layout.addWidget(self.parent.ui.image_view)
        self.parent.ui.pyqtgraph_widget.setLayout(vertical_layout)

        # profile
        self.parent.ui.profile_view = pg.PlotWidget()
        self.parent.ui.profile_view.plot()
        self.parent.legend = self.parent.ui.profile_view.addLegend()
        vertical_layout2 = QtGui.QVBoxLayout()
        vertical_layout2.addWidget(self.parent.ui.profile_view)
        self.parent.ui.profile_widget.setLayout(vertical_layout2)

    def set_item_summary_table(self, row=0, col=0, value=''):
        item = QtGui.QTableWidgetItem(str(value))
        self.parent.ui.summary_table.setItem(row, col, item)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)


class DisplayImages(object):

    def __init__(self, parent=None, recalculate_image=False):
        self.parent = parent
        self.recalculate_image = recalculate_image

        self.display_images()
        self.display_grid()

    def get_image_selected(self, recalculate_image=False):
        slider_index = self.parent.ui.file_slider.value()
        if recalculate_image:
            angle = self.parent.rotation_angle
            # rotate all images
            self.parent.data_dict['data'] = [transform.rotate(_image, angle) for _image in self.parent.data_dict_raw['data']]

        _image = self.parent.data_dict['data'][slider_index]
        return _image

    def display_images(self):
        _image = self.get_image_selected(recalculate_image=self.recalculate_image)
        _view = self.parent.ui.image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()

        first_update = False
        if self.parent.histogram_level == []:
            first_update = True
        _histo_widget = self.parent.ui.image_view.getHistogramWidget()
        self.parent.histogram_level = _histo_widget.getLevels()

        _image = np.transpose(_image)
        self.parent.ui.image_view.setImage(_image)
        self.parent.live_image = _image
        _view_box.setState(_state)

        if not first_update:
            _histo_widget.setLevels(self.parent.histogram_level[0], self.parent.histogram_level[1])

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
            adj.append([index, index + 1])
            x += grid_size
            index += 2

        # vertical lines
        y = 0
        while (y <= height):
            one_edge = [0, y]
            other_edge = [width, y]
            pos.append(one_edge)
            pos.append(other_edge)
            adj.append([index, index + 1])
            y += grid_size
            index += 2

        pos_adj_dict['pos'] = np.array(pos)
        pos_adj_dict['adj'] = np.array(adj)

        return pos_adj_dict

    def display_grid(self):
        # remove previous grid if any
        if self.parent.grid_view['item']:
            self.parent.ui.image_view.removeItem(self.parent.grid_view['item'])

        # if we want a grid
        if self.parent.ui.grid_display_checkBox.isChecked():

            grid_size = self.parent.ui.grid_size_slider.value()
            [height, width] = np.shape(self.parent.live_image)

            pos_adj_dict = self.calculate_matrix_grid(grid_size=grid_size,
                                                      height=height,
                                                      width=width)
            pos = pos_adj_dict['pos']
            adj = pos_adj_dict['adj']

            line_color = self.parent.grid_view['color']
            _transparency_value = 255 - (np.float(str(self.parent.ui.transparency_slider.value()))/100) * 255
            _list_line_color = list(line_color)
            _list_line_color[3] = _transparency_value
            line_color = tuple(_list_line_color)
            lines = np.array([line_color for n in np.arange(len(pos))],
                             dtype=[('red', np.ubyte), ('green', np.ubyte),
                                    ('blue', np.ubyte), ('alpha', np.ubyte),
                                    ('width', float)])

            grid = pg.GraphItem()
            self.parent.ui.image_view.addItem(grid)
            grid.setData(pos=pos,
                         adj=adj,
                         pen=lines,
                         symbol=None,
                         pxMode=False)
            self.parent.grid_view['item'] = grid



