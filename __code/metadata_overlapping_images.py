from IPython.core.display import HTML
from IPython.core.display import display

import numpy as np
import os
import copy
import collections
import pyqtgraph as pg
from skimage import transform
from PIL import Image

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
from __code.ui_metadata_overlapping_images import Ui_MainWindow as UiMainWindow
from __code.decorators import wait_cursor
from __code.file_handler import make_ascii_file


class MetadataOverlappingImagesUi(QMainWindow):

    data_dict = {}
    data_dict_raw = {}
    timestamp_dict = {}

    rotation_angle = 0
    histogram_level = []

    # size of tables
    guide_table_width = [300, 50]

    live_image = []
    display_ui = []

    # guide and profile pg ROIs
    list_guide_pyqt_roi = list()
    list_profile_pyqt_roi = list()
    list_table_widget_checkbox = list()

    list_metadata = []

    def __init__(self, parent=None, working_dir='', data_dict=None):

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
            (maybe hidden behind this browser!)</span>'))

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Metadata Overlapping Images")

        self.working_dir = working_dir
        self.data_dict = data_dict # Normalization data dictionary  {'file_name': [],
                                                                     #'data': [[...],[...]]],
                                                                     #'metadata': [],
                                                                     #'shape': {}}

        # untouched array of images (used to move and rotate images)
        self.data_dict_raw = copy.deepcopy(data_dict)

        # initialization
        o_initialization = Initializer(parent=self)
        # o_initialization.timestamp_dict()
        o_initialization.table()
        o_initialization.widgets()
        o_initialization.pyqtgraph()

        # display first images
        self.slider_file_changed(0)

    # ========================================================================================
    # MAIN UI EVENTs

    def previous_image_button_clicked(self):
        self.change_slider(offset = -1)

    def next_image_button_clicked(self):
        self.change_slider(offset = +1)

    def help_button_clicked(self):
        import webbrowser
        webbrowser.open("https://neutronimaging.pages.ornl.gov/en/tutorial/notebooks/metadata_overlapping_images/")

    def closeEvent(self, event=None):
        pass

    def slider_file_changed(self, slider_value):
        self.display_image()
        self.ui.image_slider_value.setText(str(slider_value))
        self.check_status_next_prev_image_button()

    def slider_file_clicked(self):
        current_slider_value = self.ui.file_slider.value()
        self.slider_file_changed(current_slider_value)

    def scale_checkbox_clicked(self, status):
        self.ui.scale_groupbox.setEnabled(status)

    def metadata_checkbox_clicked(self, status):
        self.ui.metadata_groupbox.setEnabled(status)
        self.ui.meta_label.setEnabled(status)
        self.ui.manual_metadata_name.setEnabled(status)

    def select_metadata_checkbox_clicked(self, status):
        self.ui.select_metadata_combobox.setEnabled(status)

    def metadata_list_changed(self, index):
        key_selected = self.list_metadata[index]

        for row, _file in enumerate(self.data_dict['file_name']):
            o_image = Image.open(_file)
            o_dict = dict(o_image.tag_v2)
            value = o_dict[float(key_selected)]
            self.ui.tableWidget.item(row, 1).setText("{}".format(value))


    # ========================================================================================

    def display_image(self, recalculate_image=False):
        """display the image selected by the file slider"""
        DisplayImages(parent=self, recalculate_image=recalculate_image)

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
        self.ui.image_slider_value.setText(str(new_row_selected))
        self.ui.file_slider.setValue(new_row_selected)
        self.check_status_next_prev_image_button()
        self.display_image()
        self.ui.file_slider.blockSignals(False)























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

        try:
            self.ui.all_plots_view.scene().removeItem(self.all_plots_legend)
        except Exception as e:
            print(e)

        self.all_plots_legend = self.ui.all_plots_view.addLegend()

        for _color_index_file, _index_file in enumerate(list_index_file_selected):
            _data = self.data_dict['data'][_index_file]
            for _color_index_profile, _index_profile in enumerate(list_index_profile_selected):
                legend = "File #{} - Profile #{}".format(_index_file, _index_profile)
                _color = list_rgb_profile_color[_color_index_file + _color_index_profile * nbr_file_selected]
                [x_axis, y_axis] = self.get_profile(image=np.transpose(_data), profile_roi_row=_index_profile)
                self.ui.all_plots_view.plot(x_axis, y_axis, name=legend, pen=_color)


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
            self.ui.all_plots_profiles_table.item(_row, 0).setText("Profile # {}".format(_row+1))

    # setter
    def set_item_all_plots_profile_table(self, row=0):
        item = QtGui.QTableWidgetItem("Profile # {}".format(row))
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        self.ui.all_plots_profiles_table.setItem(row, 0, item)

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

    def get_profile_dimensions(self, row=-1):
        is_x_profile_direction = self.ui.profile_direction_x_axis.isChecked()
        [x0, y0, width, height] = self.get_item_row(row=row)
        delta_profile = self.get_profile_width(row=row)

        if is_x_profile_direction:
            x_left = x0
            x_right = x0 + width

            profile_center = y0 + np.abs(np.int((height)/2.))
            y_top = profile_center - delta_profile
            y_bottom = profile_center + delta_profile

        else:
            profile_center = x0 + np.abs(np.int((width) / 2.))
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

    def __create_list_from_selection(self, selection):
        list_row_selected = []
        for _selection in selection:
            top_row = _selection.topRow()
            bottom_row = _selection.bottomRow()
            for _row in np.arange(top_row, bottom_row+1):
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






    def export_button_clicked(self):
        _export_folder = QFileDialog.getExistingDirectory(self,
                                                          directory=self.working_dir,
                                                          caption="Select Output Folder",
                                                          options=QFileDialog.ShowDirsOnly)
        if _export_folder:
            o_export = ExportProfiles(parent=self,
                                      export_folder=_export_folder)
            o_export.run()
            QtGui.QGuiApplication.processEvents()



class ExportProfiles(object):

    def __init__(self, parent=None, export_folder=''):
        self.parent = parent
        self.export_folder = export_folder

    def _create_output_file_name(self, profile_index=0):
        base_name = os.path.basename(self.parent.working_dir)
        output_file_name = os.path.join(self.export_folder, "{}_profile_{}.txt".format(base_name, profile_index+1))
        return output_file_name

    def _create_metadata(self, profile_index=0):
        metadata = ["# Counts vs pixel position"]
        metadata.append("#average counts of width of profile is used!")
        profile_dimension = self.parent.get_profile_dimensions(row=profile_index)
        is_x_profile_direction = self.parent.ui.profile_direction_x_axis.isChecked()
        x_left = profile_dimension.x_left
        x_right = profile_dimension.x_right
        y_top = profile_dimension.y_top
        y_bottom = profile_dimension.y_bottom
        metadata.append("#Profile dimension:")
        metadata.append("# * [x0, y0, x1, y1] = [{}, {}, {}, {}]".format(x_left, y_top, x_right, y_bottom))
        if is_x_profile_direction:
            metadata.append("# * integrated over y_axis")
            table_axis = ['#x_axis']
        else:
            metadata.append("# * integrated over x_axis")
            table_axis = ['#y_axis']
        nbr_files = len(self.parent.data_dict['file_name'])
        metadata.append("#List of files ({} files)".format(nbr_files))
        for _index, _file in enumerate(self.parent.data_dict['file_name']):
            metadata.append("# * {} -> col{}".format(_file, _index+1))
            table_axis.append("# col.{}".format(_index+1))
        metadata.append("#")
        metadata.append("#" + ",".join(table_axis))
        return metadata

    def _create_data(self, profile_index=0):
        all_profiles = []
        x_axis = []
        for _data in self.parent.data_dict['data']:
            [x_axis, profile] = self.parent.get_profile(image=np.transpose(_data),
                                                        profile_roi_row=profile_index)
            all_profiles.append(list(profile))

        data = []
        for _index, _row in enumerate(np.transpose(all_profiles)):
            str_row = [str(_value) for _value in _row]
            data.append("{}, ".format(x_axis[_index]) + ", ".join(str_row))

        return data

    def run(self):
        _nbr_profiles = self.parent.ui.tableWidget.rowCount()
        for _profile_index in np.arange(_nbr_profiles):
            _output_file_name = self._create_output_file_name(profile_index=_profile_index)
            metadata = self._create_metadata(profile_index=_profile_index)
            data = self._create_data(profile_index=_profile_index)
            make_ascii_file(metadata=metadata,
                            data=data,
                            output_file_name=_output_file_name,
                            dim='1d')

            display(HTML("Exported Profile file {}".format(_output_file_name)))


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
        # [x0, y0, width, height] = self.parent.get_item_row(row=self.row)
        _profile_width = self.parent.get_profile_width(row=self.row)
        is_x_profile_direction = self.parent.ui.profile_direction_x_axis.isChecked()
        # delta_profile = (_profile_width - 1) / 2.

        profile_dimension = self.parent.get_profile_dimensions(row=self.row)
        x_left = profile_dimension.x_left
        x_right = profile_dimension.x_right
        y_top = profile_dimension.y_top
        y_bottom = profile_dimension.y_bottom

        if is_x_profile_direction:

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

        for _row, _file in enumerate(list_files_short_name):
            self.parent.ui.tableWidget.insertRow(_row)
            self.set_item_table(row=_row, col=0, value=_file)
            self.set_item_table(row=_row, col=1, value="N/A", editable=True)

    def widgets(self):

        self.parent.ui.splitter.setSizes([800, 50])

        # file slider
        self.parent.ui.file_slider.setMaximum(len(self.parent.data_dict['data']) - 1)

        # update size of table columns
        nbr_columns = self.parent.ui.tableWidget.columnCount()
        for _col in range(nbr_columns):
            self.parent.ui.tableWidget.setColumnWidth(_col, self.parent.guide_table_width[_col])

        # populate list of metadata if file is a tiff
        list_metadata = self.get_list_metadata()
        if list_metadata:
            self.parent.ui.select_metadata_combobox.addItems(list_metadata)
        else: #hide widgets
            self.parent.ui.select_metadata_checkbox.setVisible(False)
            self.parent.ui.select_metadata_combobox.setVisible(False)

        # # update size of summary table
        # nbr_columns = self.parent.ui.summary_table.columnCount()
        # for _col in range(nbr_columns):
        #     self.parent.ui.summary_table.setColumnWidth(_col, self.parent.summary_table_width[_col])
        #
        # self.parent.display_ui = [self.parent.ui.display_size_label,
        #                    self.parent.ui.grid_size_slider,
        #                    self.parent.ui.display_transparency_label,
        #                    self.parent.ui.transparency_slider]

    def pyqtgraph(self):
        # image
        self.parent.ui.image_view = pg.ImageView(view=pg.PlotItem())
        self.parent.ui.image_view.ui.menuBtn.hide()
        self.parent.ui.image_view.ui.roiBtn.hide()
        vertical_layout = QtGui.QVBoxLayout()
        vertical_layout.addWidget(self.parent.ui.image_view)
        self.parent.ui.pyqtgraph_widget.setLayout(vertical_layout)

    def set_item_all_plot_file_name_table(self, row=0, value=''):
        item = QtGui.QTableWidgetItem(str(value))
        self.parent.ui.all_plots_file_name_table.setItem(row, 0, item)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

    def set_item_table(self, row=0, col=0, value='', editable=False):
        item = QtGui.QTableWidgetItem(str(value))
        self.parent.ui.tableWidget.setItem(row, col, item)
        if not editable:
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

    def get_list_metadata(self):
        first_file = self.parent.data_dict['file_name'][0]
        [_, ext] = os.path.splitext(os.path.basename(first_file))
        if ext in [".tif", ".tiff"]:
            o_image0 = Image.open(first_file)
            info = collections.OrderedDict(sorted(o_image0.tag_v2.items()))
            list_metadata = []
            list_key = []
            for tag, value in info.items():
                list_metadata.append("{} -> {}".format(tag, value))
                list_key.append(tag)
            self.parent.list_metadata = list_key
            return list_metadata
        else:
            return []

class DisplayImages(object):

    def __init__(self, parent=None, recalculate_image=False):
        self.parent = parent
        self.recalculate_image = recalculate_image

        self.display_images()
        # self.display_grid()

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



