from IPython.core.display import HTML
from IPython.core.display import display

import numpy as np
import os
import copy
import collections

from qtpy.QtWidgets import QFileDialog, QMainWindow, QTableWidgetSelectionRange, QTableWidgetItem, \
    QSpacerItem, QComboBox, QHBoxLayout, QSizePolicy, QCheckBox, QWidget
from qtpy import QtCore
from qtpy.QtGui import QGuiApplication

from __code import load_ui
from __code import interact_me_style, normal_style
from __code._utilities.color import Color
from __code._utilities.table_handler import TableHandler
from __code.profile.initialization import Initializer
from __code.profile.display import DisplayImages
from __code.profile.export import ExportProfiles, ExportAverageROI
from __code.profile.guide_and_profile_rois_handler import GuideAndProfileRoisHandler


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
    grid_view = {'pos'  : None,
                 'adj'  : None,
                 'item' : None,
                 'color': (0, 0, 255, 255, 1)}

    profile_color = (0, 255, 0, 255, 1)

    display_ui = []

    # guide and profile pg ROIs
    list_guide_pyqt_roi = list()
    list_profile_pyqt_roi = list()
    list_table_widget_checkbox = list()
    default_guide_roi = {'x0'               : 0, 'y0': 0, 'width': 200, 'height': 800,
                         'isChecked'        : True,
                         'color_activated'  : 'r',
                         'color_deactivated': 'b'}
    previous_active_row = -1  # use to deactivated the guide and profile roi

    # default_guide_table_values = {'isChecked': True, 'x0': 0, 'y0': 0,
    #                               'width': 200, 'height': 200}
    default_profile_width_values = np.arange(1, 300, 2)

    # remove-me
    test_roi = None

    def __init__(self, parent=None, working_dir='', data_dict=None):

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that popped up \
            (maybe hidden behind this browser!)</span>'))

        QMainWindow.__init__(self, parent=parent)

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_profile.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Profile")

        self.working_dir = working_dir
        self.data_dict = data_dict  # Normalization data dictionary  {'file_name': [],
        # 'data': [[...],[...]]],
        # 'metadata': [],
        # 'shape': {}}
        self.list_filenames = data_dict['file_name']

        # untouched array of images (used to move and rotate images)
        self.data_dict_raw = copy.deepcopy(data_dict)

        # initialization
        o_initialization = Initializer(parent=self)
        o_initialization.all()

        # display first images
        self.slider_file_changed(-1)

    def check_widgets(self):
        if self._we_can_enable_export_profiles():
            self.ui.export_button.setStyleSheet(interact_me_style)
            enable_button = True
        else:
            self.ui.export_button.setStyleSheet(normal_style)
            enable_button = False
        self.ui.export_button.setEnabled(enable_button)

    def _we_can_enable_export_profiles(self):

        # if no profile, we can't enable export
        o_table = TableHandler(table_ui=self.ui.tableWidget)
        nbr_row = o_table.row_count()
        if nbr_row == 0:
            return False

        return True

    # main methods
    def remove_all_guides(self):
        # remove all the guides
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
        self.ui.profile_view.clear()
        if nbr_row == 0:
            return

        image = self.live_image
        color = Color()
        list_rgb_profile_color = color.get_list_rgb(nbr_color=nbr_row)

        self.legend = self.ui.profile_view.addLegend()

        for _row in np.arange(nbr_row):
            [x_axis, profile] = self.get_profile(image=image, profile_roi_row=_row)
            _label = ' Profile #{}'.format(_row + 1)
            _color = list_rgb_profile_color[_row]
            self.ui.profile_view.plot(x_axis, profile,
                                      name=_label,
                                      pen=_color)

    def update_all_plots(self):
        list_index_file_selected = self.get_all_plots_files_index_selected()
        list_index_profile_selected = self.get_all_plots_profiles_selected()
        nbr_profile = len(list_index_profile_selected)
        nbr_file_selected = len(list_index_file_selected)
        color = Color()
        list_rgb_profile_color = color.get_list_rgb(nbr_color=(nbr_profile * nbr_file_selected))
        self.ui.all_plots_view.clear()

        if nbr_profile == 0:
            return

        self.all_plots_legend = self.ui.all_plots_view.addLegend()

        for _color_index_file, _index_file in enumerate(list_index_file_selected):
            _data = self.data_dict['data'][_index_file]
            for _color_index_profile, _index_profile in enumerate(list_index_profile_selected):
                legend = "File #{} - Profile #{}".format(_index_file, _index_profile)
                _color = list_rgb_profile_color[_color_index_file + _color_index_profile * nbr_file_selected]
                [x_axis, y_axis] = self.get_profile(image=np.transpose(_data), profile_roi_row=_index_profile)
                self.ui.all_plots_view.plot(x_axis, y_axis, name=legend, pen=_color)

    def display_image(self, recalculate_image=False):
        """display the image selected by the file slider"""
        o_image = DisplayImages(parent=self, recalculate_image=recalculate_image)

    def remove_row(self, row=-1):

        if row == -1:
            return

        # maint tab
        self.ui.tableWidget.removeRow(row)
        self.ui.tableWidget_2.removeRow(row)
        self.ui.image_view.removeItem(self.list_guide_pyqt_roi[row])
        self.list_guide_pyqt_roi.remove(self.list_guide_pyqt_roi[row])
        self.ui.image_view.removeItem(self.list_profile_pyqt_roi[row])
        self.list_profile_pyqt_roi.remove(self.list_profile_pyqt_roi[row])
        # self.list_table_widget_checkbox.remove(self.list_profile_pyqt_roi[row])

        # all plots tab
        self.ui.all_plots_profiles_table.removeRow(row)
        self.rename_all_plots_profiles_table()

        nbr_row = self.ui.tableWidget.rowCount()
        if row == nbr_row:
            row -= 1

        if nbr_row > 0:
            nbr_col = self.ui.tableWidget.columnCount()
            new_selection = QTableWidgetSelectionRange(row, 0, row, nbr_col - 1)
            self.ui.tableWidget.setRangeSelected(new_selection, True)
            new_selection_2 = QTableWidgetSelectionRange(row, 0, row, 1)
            self.ui.tableWidget_2.setRangeSelected(new_selection_2, True)

    def update_guide_roi_using_guide_table(self, row=-1):
        [x0, y0, width, height] = self.get_item_row(row=row)
        roi_ui = self.list_guide_pyqt_roi[row]
        roi_ui.blockSignals(True)
        roi_ui.setPos((x0, y0))
        roi_ui.setSize((width, height))
        roi_ui.blockSignals(False)

    def update_profile_rois(self, row=-1):
        if row == -1:  # update all of them

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
        return False

    def update_guide_table_using_guide_rois(self):
        for _row, _roi in enumerate(self.list_guide_pyqt_roi):
            if self.is_row_enabled(row=_row):
                region = _roi.getArraySlice(self.live_image,
                                            self.ui.image_view.imageItem)

                x0 = region[0][0].start
                x1 = region[0][0].stop
                y0 = region[0][1].start
                y1 = region[0][1].stop

                width = np.abs(x1 - x0) - 1
                height = np.abs(y1 - y0) - 1

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
        full_range = QTableWidgetSelectionRange(0, 0, nbr_row - 1, nbr_col - 1)
        self.ui.tableWidget.setRangeSelected(full_range, False)
        new_selection = QTableWidgetSelectionRange(row, 0, row, nbr_col - 1)
        self.ui.tableWidget.setRangeSelected(new_selection, True)
        self.ui.tableWidget.blockSignals(False)

        self.ui.tableWidget_2.blockSignals(True)
        self.ui.tableWidget_2.insertRow(row)
        self.ui.tableWidget_2.setRowHeight(row, self.guide_table_height)
        self.set_item_profile_table(row=row)

        # select new entry
        nbr_col = self.ui.tableWidget_2.columnCount()
        full_range = QTableWidgetSelectionRange(0, 0, nbr_row - 1, nbr_col - 1)
        self.ui.tableWidget_2.setRangeSelected(full_range, False)
        new_selection = QTableWidgetSelectionRange(row, 0, row, nbr_col - 1)
        self.ui.tableWidget_2.setRangeSelected(new_selection, True)
        self.ui.tableWidget_2.blockSignals(False)

        # all plots tab
        self.ui.all_plots_profiles_table.blockSignals(True)
        self.ui.all_plots_profiles_table.insertRow(row)
        self.set_item_all_plots_profile_table(row=row)
        self.ui.all_plots_profiles_table.blockSignals(False)
        self.rename_all_plots_profiles_table()

    def rename_all_plots_profiles_table(self):
        """rename all the profile name"""
        nbr_row = self.ui.tableWidget.rowCount()
        for _row in np.arange(nbr_row):
            self.ui.all_plots_profiles_table.item(_row, 0).setText("Profile # {}".format(_row + 1))

    # setter
    def set_item_all_plots_profile_table(self, row=0):
        item = QTableWidgetItem("Profile # {}".format(row))
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        self.ui.all_plots_profiles_table.setItem(row, 0, item)

    def set_item_profile_table(self, row=0):
        spacerItem_left = QSpacerItem(408, 20, QSizePolicy.Expanding, QSizePolicy.Expanding)
        widget = QComboBox()
        widget.addItems(self.default_profile_width_values)
        widget.blockSignals(True)
        widget.currentIndexChanged.connect(self.profile_width_changed)
        spacerItem_right = QSpacerItem(408, 20, QSizePolicy.Expanding, QSizePolicy.Expanding)
        hori_layout = QHBoxLayout()
        hori_layout.addItem(spacerItem_left)
        hori_layout.addWidget(widget)
        hori_layout.addItem(spacerItem_right)
        cell_widget = QWidget()
        cell_widget.setLayout(hori_layout)
        self.ui.tableWidget_2.setCellWidget(row, 0, cell_widget)
        widget.blockSignals(False)

    def set_item_main_table(self, row=0, col=0, value=''):
        if col == 0:
            spacerItem_left = QSpacerItem(408, 20, QSizePolicy.Expanding, QSizePolicy.Expanding)
            widget = QCheckBox()
            widget.blockSignals(True)
            self.list_table_widget_checkbox.insert(row, widget)
            widget.stateChanged.connect(self.guide_state_changed)
            spacerItem_right = QSpacerItem(408, 20, QSizePolicy.Expanding, QSizePolicy.Expanding)
            hori_layout = QHBoxLayout()
            hori_layout.addItem(spacerItem_left)
            hori_layout.addWidget(widget)
            hori_layout.addItem(spacerItem_right)
            cell_widget = QWidget()
            cell_widget.setLayout(hori_layout)
            if value is True:
                widget.setCheckState(QtCore.Qt.Checked)
            else:
                widget.setCheckState(QtCore.Qt.Unchecked)
            self.ui.tableWidget.setCellWidget(row, col, cell_widget)
            widget.blockSignals(False)
        else:
            # self.ui.tableWidget.blockSignals(True)
            item = QTableWidgetItem(str(value))
            self.ui.tableWidget.setItem(row, col, item)
            # self.ui.tableWidget.blockSignals(False)

    def get_full_roi_dimension(self, row=-1):   
        """return the dimension of the full region surrounding the ROI (red rectangle)"""
        [x0, y0, width, height] = self.get_item_row(row=row)
        
        roi = collections.namedtuple('roi', ['x0', 'y0', 'width', 'height'])
        result = roi(x0, y0, width, height)
        return result

    def get_profile_dimensions(self, row=-1):
        is_x_profile_direction = self.ui.profile_direction_x_axis.isChecked()
        [x0, y0, width, height] = self.get_item_row(row=row)
        delta_profile = self.get_profile_width(row=row)

        if is_x_profile_direction:
            x_left = x0
            x_right = x0 + width

            profile_center = y0 + np.abs(int((height) / 2.))
            y_top = profile_center - delta_profile
            y_bottom = profile_center + delta_profile

        else:
            profile_center = x0 + np.abs(int((width) / 2.))
            x_left = profile_center - delta_profile
            x_right = profile_center + delta_profile

            y_top = y0
            y_bottom = y0 + height

        Profile = collections.namedtuple('Profile', ['x_left', 'x_right', 'y_top', 'y_bottom', 'profile_center'])
        result = Profile(x_left, x_right, y_top, y_bottom, profile_center)
        return result

    def get_profile(self, image=[], profile_roi_row=-1):
        is_x_profile_direction = self.ui.profile_direction_x_axis.isChecked()

        profile_dimension = self.get_profile_dimensions(row=profile_roi_row)
        x_left = profile_dimension.x_left
        x_right = profile_dimension.x_right
        y_top = profile_dimension.y_top
        y_bottom = profile_dimension.y_bottom

        if is_x_profile_direction:
            mean_axis = 1
            x_axis = np.arange(x_left, x_right)

        else:
            mean_axis = 0
            x_axis = np.arange(y_top, y_bottom)

        _data = image[x_left: x_right, y_top:y_bottom]  # because pyqtgrpah display transpose images
        profile = np.mean(_data, axis=mean_axis)
        return [x_axis, profile]

    def get_profile_width(self, row=0):
        _widget = self.ui.tableWidget_2.cellWidget(row, 0).children()[1]
        return int(str(_widget.currentText()))

    def get_item_row(self, row=0):
        x0 = int(str(self.ui.tableWidget.item(row, 1).text()))
        y0 = int(str(self.ui.tableWidget.item(row, 2).text()))
        width = int(str(self.ui.tableWidget.item(row, 3).text()))
        height = int(str(self.ui.tableWidget.item(row, 4).text()))
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

    def __create_list_from_selection(self, selection):
        list_row_selected = []
        for _selection in selection:
            top_row = _selection.topRow()
            bottom_row = _selection.bottomRow()
            for _row in np.arange(top_row, bottom_row + 1):
                list_row_selected.append(_row)
        return list_row_selected

    def get_all_plots_profiles_selected(self):
        selection = self.ui.all_plots_profiles_table.selectedRanges()
        return self.__create_list_from_selection(selection)

    def get_all_plots_files_index_selected(self):
        selection = self.ui.all_plots_file_name_table.selectedRanges()
        return self.__create_list_from_selection(selection)

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

        try:
            self._highlights_guide_profile_pyqt_roi(row=previous_active_row, status='deactivated')
            self._highlights_guide_profile_pyqt_roi(row=row, status='activated')
        except:
            pass

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
        if tab_index == 1:  # display all plots
            self.update_all_plots()

    def guide_changed(self):
        self.update_guide_table_using_guide_rois()
        self.update_profile_rois()

    def table_widget_selection_changed(self):
        self.ui.tableWidget_2.blockSignals(True)
        nbr_col = self.ui.tableWidget_2.columnCount()
        nbr_row = self.ui.tableWidget_2.rowCount()
        full_range = QTableWidgetSelectionRange(0, 0, nbr_row - 1, nbr_col - 1)
        self.ui.tableWidget_2.setRangeSelected(full_range, False)
        row = self.get_selected_row()
        new_selection = QTableWidgetSelectionRange(row, 0, row, nbr_col - 1)
        self.ui.tableWidget_2.setRangeSelected(new_selection, True)
        self.highlight_guide_profile_pyqt_rois(row=row)
        self.ui.tableWidget_2.blockSignals(False)
        self.previous_active_row = row

    def table_widget_2_selection_changed(self):
        self.ui.tableWidget.blockSignals(True)
        nbr_col = self.ui.tableWidget.columnCount()
        nbr_row = self.ui.tableWidget.rowCount()
        full_range = QTableWidgetSelectionRange(0, 0, nbr_row - 1, nbr_col - 1)
        self.ui.tableWidget.setRangeSelected(full_range, False)
        row = self.get_selected_row(source='tableWidget_2')
        new_selection = QTableWidgetSelectionRange(row, 0, row, nbr_col - 1)
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
        self.check_widgets()

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

    # @wait_cursor
    def right_rotation_slow_clicked(self):
        self.rotation_angle -= 0.1
        self.display_image(recalculate_image=True)
        self.display_profiles()

    # @wait_cursor
    def left_rotation_slow_clicked(self):
        self.rotation_angle += 0.1
        self.display_image(recalculate_image=True)
        self.display_profiles()

    # @wait_cursor
    def right_rotation_fast_clicked(self):
        self.rotation_angle -= 1
        self.display_image(recalculate_image=True)
        self.display_profiles()

    # @wait_cursor
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
        self.check_widgets()

    def remove_row_button_clicked(self):
        selected_row = self.get_selected_row()
        self.remove_row(row=selected_row)
        self.display_profiles()
        self.check_widgets()

    def profile_along_axis_changed(self):
        self.update_profile_rois()
        self.display_profiles()

    def export_button_clicked(self):
        _export_folder = QFileDialog.getExistingDirectory(self,
                                                          directory=self.working_dir,
                                                          caption="Select Output Folder",
                                                          options=QFileDialog.ShowDirsOnly)
        if _export_folder:
            o_export = ExportProfiles(parent=self,
                                      export_folder=_export_folder)
            o_export.run()
 
            o_average = ExportAverageROI(parent=self,
                                         export_folder=_export_folder)
            o_average.run()

            QGuiApplication.processEvents()

    def previous_image_button_clicked(self):
        self.change_slider(offset=-1)
        # self.display_measurement_profiles()

    def next_image_button_clicked(self):
        self.change_slider(offset=+1)
        # self.display_measurement_profiles()

    def help_button_clicked(self):
        import webbrowser
        webbrowser.open("https://neutronimaging.pages.ornl.gov/en/tutorial/notebooks/profile/")

    def closeEvent(self, event=None):
        pass
