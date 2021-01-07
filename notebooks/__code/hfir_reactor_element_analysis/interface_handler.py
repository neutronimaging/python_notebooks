from qtpy.QtWidgets import QMainWindow, QVBoxLayout, QProgressBar, QApplication
import os
import numpy as np

from __code import load_ui
from __code.hfir_reactor_element_analysis.initialization import Initialization
from __code.hfir_reactor_element_analysis.event_handler import EventHandler


class InterfaceHandler:

    def __init__(self, working_dir=None, o_selection=None):
        o_interface = Interface(o_selection=o_selection,
                                working_dir=working_dir)
        o_interface.show()
        self.o_interface = o_interface


class Interface(QMainWindow):

    def __init__(self, parent=None, o_selection=None, working_dir=None):
        self.o_selection = o_selection
        self.o_pandas = o_selection.pandas_obj
        self.working_dir = working_dir

        super(Interface, self).__init__(parent)

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_hfir_reactor_element_fitting.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Data fitting")

        o_init = Initialization(parent=self)
        o_init.matplotlib()
        o_init.widgets()

    def list_of_images_selection_changed(self):
        selection = self.ui.listWidget.selectedItems()
        list_file_selected = [_item.text() for _item in selection]
        pandas_obj = self.o_selection.pandas_obj

        x_axis = np.array(pandas_obj.index)
        list_y_axis = []
        for _file in list_file_selected:
            _y_axis = np.array(pandas_obj[_file])
            list_y_axis.append(_y_axis)

        self.top_plot.axes.clear()
        self.top_plot.draw()

        plot_type = '-'
        if self.ui.plus_radioButton.isChecked():
            plot_type = '+'
        elif self.ui.point_radioButton.isChecked():
            plot_type = "."

        for _index, _y_axis in enumerate(list_y_axis):
            self.top_plot.axes.plot(x_axis, _y_axis, plot_type, label=list_file_selected[_index])
            self.top_plot.axes.legend()
            self.top_plot.axes.set_title("Profile of selected images")
            self.top_plot.draw()

    def plot_type_changed(self):
        self.list_of_images_selection_changed()

    def list_of_images_right_click(self, position=None):
        o_event = EventHandler(parent=self)
        o_event.list_of_images_right_click()
