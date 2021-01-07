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

    # event handler
    def list_of_images_selection_changed(self):
        o_event = EventHandler(parent=self)
        o_event.list_of_images_selection_changed()

    def plot_type_changed(self):
        self.list_of_images_selection_changed()

    def list_of_images_right_click(self, position=None):
        o_event = EventHandler(parent=self)
        o_event.list_of_images_right_click()

    def automatic_fit_clicked(self):
        # range of files to use to fit
        file_range = self.ui.file_range_slider.getRange()
        angle_range = self.ui.angle_range_slider.getRange()

        list_of_files = self.o_selection.column_labels[1:]
        list_of_file_to_use = list_of_files[file_range[0]: file_range[1]+1]

        print(f"list_of_files_to_use: {list_of_file_to_use}")
