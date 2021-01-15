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
        low_threshold = self.parent.ui.low_threshold_slider.value()
        high_threshold = self.parent.ui.high_threshold_slider.value()

        list_of_images = self.parent.o_selection.column_labels[1:]
        global_list_of_xy_max = {}

        self.parent.eventProgress.setMaximum(len(list_of_images))
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)

        pandas_obj = self.parent.o_selection.pandas_obj
        working_x_axis = np.array(pandas_obj.index)
        for _file_index, _file in enumerate(list_of_images):
            working_y_axis = np.array(pandas_obj[_file])
            _dict = self.calculate_list_of_local_max(file_index=_file_index,
                                                     low_threshold=low_threshold,
                                                     high_threshold=high_threshold,
                                                     working_x_axis=working_x_axis,
                                                     working_y_axis=working_y_axis)
            _dict = {'x': _dict['x'],
                     'y': _dict['y']}
            global_list_of_xy_max[_file] = _dict

            self.parent.eventProgress.setValue(_file_index+1)
            QtGui.QGuiApplication.processEvents()

        self.parent.global_list_of_xy_max = global_list_of_xy_max
        self.parent.eventProgress.setVisible(False)

    def calculate_list_of_local_max(self, file_index=0,
                                    low_threshold=0, high_threshold=0,
                                    working_x_axis=None, working_y_axis=None):
        we_are_in_high_region = False
        we_are_in_low_region = False
        we_are_in_threshold_region = False

        we_were_in_high_region = False
        we_were_in_low_region = False
        we_were_in_threshold_region = False

        list_of_x_of_local_max = []
        list_of_y_max = []
        local_y_max = 0
        x_of_local_max = 0
        for _x_value, _y_value in zip(working_x_axis, working_y_axis):

            #     if _x_value > 2.5:
            #         pdb.set_trace()

            if _y_value < low_threshold:
                # in low region, nothing to record
                we_are_in_low_region = True
                we_are_in_high_region = False
                we_are_in_threshold_region = False

                we_were_in_low_region = True

                if local_y_max != 0:
                    list_of_x_of_local_max.append(x_of_local_max)
                    list_of_y_max.append(local_y_max)
                    local_y_max = 0

                continue

            if _y_value > low_threshold:

                if _y_value < high_threshold:
                    # in threshold region

                    if we_were_in_low_region:
                        # we are coming back up
                        we_are_in_low_region = False
                        we_are_in_threshold_region = True
                        continue

                    if we_were_in_high_region:
                        # we are going down, we need to record the xmax we found before leaving the region
                        list_of_x_of_local_max.append(x_of_local_max)
                        list_of_y_max.append(local_y_max)
                        we_are_in_high_region = False
                        we_are_in_threshold_region = True

                        local_y_max = 0  # reset local y max

                        continue

                if _y_value > high_threshold:
                    # in top region

                    we_are_in_high_region = True
                    we_are_in_low_region = False
                    we_are_in_threshold_region = False

                    if _y_value > local_y_max:
                        x_of_local_max = _x_value
                        local_y_max = _y_value

                    we_were_in_high_region = True

        return {'x': list_of_x_of_local_max,
                'y': list_of_y_max}
