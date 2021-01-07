from qtpy.QtWidgets import QMainWindow, QVBoxLayout, QProgressBar, QApplication
import os

from __code import load_ui
from __code.hfir_reactor_element_analysis.initialization import Initialization


class InterfaceHandler:

    def __init__(self, working_dir=None, o_pandas=None):
        o_interface = Interface(o_pandas=o_pandas,
                                working_dir=working_dir)
        o_interface.show()
        self.o_interface = o_interface


class Interface(QMainWindow):

    def __init__(self, parent=None, o_pandas=None, working_dir=None):
        self.o_pandas = o_pandas
        self.workind_dir = working_dir

        super(Interface, self).__init__(parent)

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_hfir_reactor_element_fitting.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Data fitting")

        o_init = Initialization(parent=self)
        o_init.matplotlib()
