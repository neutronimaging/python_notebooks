from qtpy import QtGui
from qtpy.QtWidgets import QMenu
import numpy as np


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def list_of_images_right_click(self):
        menu = QMenu(self.parent)
        unsellect_all = menu.addAction("Unselect all")
        action = menu.exec_(QtGui.QCursor.pos())

        if action == unsellect_all:
            self.unselect_all()

    def unselect_all(self):
        self.parent.ui.listWidget.clearSelection()

    def list_of_images_selection_changed(self):
        selection = self.parent.ui.listWidget.selectedItems()
        list_file_selected = [_item.text() for _item in selection]
        pandas_obj = self.parent.o_selection.pandas_obj

        x_axis = np.array(pandas_obj.index)
        list_y_axis = []
        for _file in list_file_selected:
            _y_axis = np.array(pandas_obj[_file])
            list_y_axis.append(_y_axis)

        self.parent.profiles_plot.axes.clear()
        self.parent.profiles_plot.draw()

        plot_type = '-'
        if self.parent.ui.plus_radioButton.isChecked():
            plot_type = '+'
        elif self.parent.ui.point_radioButton.isChecked():
            plot_type = "."

        for _index, _y_axis in enumerate(list_y_axis):
            self.parent.profiles_plot.axes.plot(x_axis, _y_axis, plot_type, label=list_file_selected[_index])
            self.parent.profiles_plot.axes.legend()
            self.parent.profiles_plot.axes.set_title("Profile of selected images")

        if self.parent.global_list_of_xy_max:
            for _file in list_file_selected:
                x_max = self.parent.global_list_of_xy_max[_file]['x']
                y_max = self.parent.global_list_of_xy_max[_file]['y']
                self.parent.profiles_plot.axes.plot(x_max, y_max, '*r')

        # thresholds
        threshold = self.parent.ui.threshold_slider.value()
        self.parent.profiles_plot.axes.axhline(threshold, linestyle='--', color='red')
        self.parent.profiles_plot.draw()

    def get_profile_of_file_index(self, file_index):
        pandas_obj = self.parent.o_pandas
        file_index_name = self.parent.o_pandas.columns[file_index]
        profile_of_file = pandas_obj[file_index_name]
        return profile_of_file

    def get_profile_of_selected_files(self):
        list_file_index_selected = self.parent.get_list_file_index_selected()
        list_profiles = []
        for _file_index in list_file_index_selected:
            _profile = self.get_profile_of_file_index(_file_index)
            list_profiles.append(_profile)
        return list_profiles

    def threshold_clicked(self):
        self.parent.list_of_images_selection_changed()

    def threshold_moved(self, value):
        self.parent.list_of_images_selection_changed()

    def calculate_elements_position(self):
        list_of_images = self.parent.o_selection.column_labels[1:]
        global_list_of_xy_max = {}

        self.parent.eventProgress.setMaximum(len(list_of_images))
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)

        pandas_obj = self.parent.o_selection.pandas_obj
        self.working_x_axis = np.array(pandas_obj.index)

        for _file_index, _file in enumerate(list_of_images):
            working_y_axis = np.array(pandas_obj[_file])
            _dict = self.calculate_list_of_local_max(working_y_axis=working_y_axis)
            _dict = {'x': _dict['x'],
                     'y': _dict['y']}
            global_list_of_xy_max[_file] = _dict

            self.parent.eventProgress.setValue(_file_index+1)
            QtGui.QGuiApplication.processEvents()

        self.parent.global_list_of_xy_max = global_list_of_xy_max
        self.parent.eventProgress.setVisible(False)

    def calculate_list_of_local_max(self, working_y_axis=None):

        working_x_axis = self.working_x_axis
        threshold = self.parent.ui.threshold_slider.value()

        list_of_x_of_local_max = []
        list_of_y_max = []
        local_y_max = 0
        x_of_local_max = 0
        minimum_number_of_points_to_high_region = self.parent.ui.minimum_number_of_points_spinBox.value()
        number_of_points_in_current_high_region = 0
        for _x_value, _y_value in zip(working_x_axis, working_y_axis):

            if _y_value < threshold:

                if local_y_max != 0:
                    if number_of_points_in_current_high_region >= minimum_number_of_points_to_high_region:
                        list_of_x_of_local_max.append(x_of_local_max)
                        list_of_y_max.append(local_y_max)
                        local_y_max = 0

                number_of_points_in_current_high_region = 0
                continue

            else:

                if _y_value > local_y_max:
                    x_of_local_max = _x_value
                    local_y_max = _y_value

                number_of_points_in_current_high_region += 1

        return {'x': list_of_x_of_local_max,
                'y': list_of_y_max}

    def populate_elements_position_tab(self):
        global_list_of_xy_max = self.parent.global_list_of_xy_max
        list_of_images = self.parent.o_selection.column_labels[1:]

        self.parent.elements_position.axes.clear()
        self.parent.elements_position.draw()

        plot_type = "."

        for _file_index, _file in enumerate(list_of_images):
            x_axis = global_list_of_xy_max[_file]['x']
            y_axis = np.ones((len(x_axis)))*(_file_index+1)
            self.parent.elements_position.axes.plot(x_axis, y_axis, plot_type)

        self.parent.elements_position.draw()
