from qtpy import QtGui
from qtpy.QtWidgets import QMenu
import numpy as np

from __code._utilities.array import get_n_random_int_of_max_value_m, reject_outliers


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

        self.parent.top_plot.axes.clear()
        self.parent.top_plot.draw()

        plot_type = '-'
        if self.parent.ui.plus_radioButton.isChecked():
            plot_type = '+'
        elif self.parent.ui.point_radioButton.isChecked():
            plot_type = "."

        for _index, _y_axis in enumerate(list_y_axis):
            self.parent.top_plot.axes.plot(x_axis, _y_axis, plot_type, label=list_file_selected[_index])
            self.parent.top_plot.axes.legend()
            self.parent.top_plot.axes.set_title("Profile of selected images")
            self.parent.top_plot.draw()

        self.parent.automatic_a_value_estimate()
        self.parent.automatic_b_value_estimate()

    def get_profile_of_file_index(self, file_index):
        pandas_obj = self.parent.o_pandas
        file_index_name = self.parent.o_pandas.columns[file_index]
        profile_of_mid_file_name = pandas_obj[file_index_name]
        return profile_of_mid_file_name

    def get_profile_of_selected_files(self):
        list_file_index_selected = self.parent.get_list_file_index_selected()
        list_of_files = self.parent.o_selection.column_labels[1:]
        list_profiles = []
        pandas_obj = self.parent.o_selection.pandas_obj
        for _file_index in list_file_index_selected:
            _profile = self.get_profile_of_file_index(_file_index)
            list_profiles.append(_profile)
        return list_profiles

    def calculate_a_value_estimate(self):
        list_profile_of_selected_files = self.get_profile_of_selected_files()

        list_max_y = [np.nanmax(_array) for _array in list_profile_of_selected_files]
        list_min_y = [np.nanmin(_array) for _array in list_profile_of_selected_files]

        list_max_y_without_outliers = reject_outliers(array=list_max_y)
        max_y = np.nanmean(list_max_y_without_outliers)

        list_min_y_without_outliers = reject_outliers(array=list_min_y)
        min_y = np.nanmean(list_min_y_without_outliers)

        self.parent.ui.automatic_initial_guess_a_lineEdit.setText("{:.2f}".format(max_y - min_y))

    def calculate_b_value_estimate(self):
        list_profile_of_selected_files = self.get_profile_of_selected_files()
        list_mean_y = [np.nanmean(_array) for _array in list_profile_of_selected_files]
        list_mean_y_without_outliers = reject_outliers(array=list_mean_y)
        mean_y = np.nanmean(list_mean_y_without_outliers)
        self.parent.ui.automatic_initial_guess_b_lineEdit.setText("{:.2f}".format(mean_y))
