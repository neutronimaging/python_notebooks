from qtpy.QtWidgets import QMainWindow
import os

from __code import load_ui
from __code.extract_evenly_spaced_files.interface_initialization import InterfaceInitialization


class Interface:

    def __init__(self, o_extract=None):
        o_interface_handler = InterfaceHandler(o_extract=o_extract)
        o_interface_handler.show()


class InterfaceHandler(QMainWindow):

    basename_list_of_files_that_will_be_extracted = None

    def __init__(self, parent=None, o_extract=None):
        self.parent = parent
        self.o_extract = o_extract
        self.basename_list_of_files_that_will_be_extracted = \
            o_extract.basename_list_of_files_that_will_be_extracted

        super(InterfaceHandler, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_extract_evenly_spaced_files.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Extract Evenly Spaced Files")

        o_init = InterfaceInitialization(parent=self)
        o_init.all()
