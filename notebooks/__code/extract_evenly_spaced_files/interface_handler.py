from qtpy.QtWidgets import QMainWindow
import os

from __code import load_ui


class Interface:

    def __init__(self, o_extract=None):
        o_interface_handler = InterfaceHandler(o_extract=o_extract)
        o_interface_handler.show()


class InterfaceHandler(QMainWindow):

    def __init__(self, parent=None, o_extract=None):
        self.parent = parent
        self.o_extract = o_extract

        super(InterfaceHandler, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_extract_evenly_spaced_files.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Extract Evenly Spaced Files")
