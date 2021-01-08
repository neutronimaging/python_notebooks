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

    def calculate_a_value_estimate(self):
        pandas_obj = self.parent.o_pandas
        mid_file_name = self.parent.o_pandas.columns[np.int(len(self.parent.o_pandas.columns)/2)]
        profile_of_mid_file_name = pandas_obj[mid_file_name]
        max_y = np.max(profile_of_mid_file_name)
        min_y = np.min(profile_of_mid_file_name)
        self.parent.ui.automatic_initial_guess_a_lineEdit.setText(str(max_y - min_y))

    def calculate_b_value_estimate(self):
        self.parent.ui.automatic_initial_guess_b_lineEdit.setText("work in progress!")