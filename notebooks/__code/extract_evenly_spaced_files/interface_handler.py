from qtpy.QtWidgets import QMainWindow
import os

from __code import load_ui
from __code._utilities.list_widget import ListWidget

from __code.extract_evenly_spaced_files.interface_initialization import InterfaceInitialization
from __code.extract_evenly_spaced_files.event_handler import EventHandler


class Interface:

    def __init__(self, o_extract=None):
        o_interface_handler = InterfaceHandler(o_extract=o_extract)
        o_interface_handler.show()
        o_interface_handler.init_loading()


class InterfaceHandler(QMainWindow):

    basename_list_of_files_that_will_be_extracted = None
    list_of_files_that_will_be_extracted = None
    list_data = None

    def __init__(self, parent=None, o_extract=None):
        self.parent = parent
        self.o_extract = o_extract
        self.basename_list_of_files_that_will_be_extracted = \
            o_extract.basename_list_of_files_that_will_be_extracted
        self.list_of_files_that_will_be_extracted = o_extract.list_of_files_to_extract

        super(InterfaceHandler, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_extract_evenly_spaced_files.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Extract Evenly Spaced Files")

        o_init = InterfaceInitialization(parent=self)
        o_init.all()

    def init_loading(self):
        o_event = EventHandler(parent=self)
        o_event.load_files()
        o_event.select_first_file()

    # event handler
    def image_selected_changed(self):
        o_event = EventHandler(parent=self)
        o_event.image_selected_changed()

    def previous_image_clicked(self):
        o_list = ListWidget(ui=self.ui.list_of_files_listWidget)
        o_list.select_previous_element()
        self.check_previous_next_image_status()

    def next_image_clicked(self):
        o_list = ListWidget(ui=self.ui.list_of_files_listWidget)
        o_list.select_next_element()
        self.check_previous_next_image_status()

    def check_previous_next_image_status(self):
        previous_status = True
        next_status = True

        o_list = ListWidget(ui=self.ui.list_of_files_listWidget)
        index_image_selected = o_list.get_current_row()
        if index_image_selected == 0:
            previous_status = False

        nbr_elements = o_list.get_number_elements()
        if index_image_selected == (nbr_elements-1):
            next_status = False

        self.ui.previous_image_pushButton.setEnabled(previous_status)
        self.ui.next_image_pushButton.setEnabled(next_status)

