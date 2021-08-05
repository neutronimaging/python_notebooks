from qtpy.QtWidgets import QMainWindow
import os
import logging

from __code import load_ui
from __code._utilities.list_widget import ListWidget

from __code.extract_evenly_spaced_files.interface_initialization import InterfaceInitialization
from __code.extract_evenly_spaced_files.event_handler import EventHandler
from __code.extract_evenly_spaced_files.get import Get
from __code.extract_evenly_spaced_files.statistics import Statistics


class Interface:

    def __init__(self, o_extract=None):
        o_interface_handler = InterfaceHandler(o_extract=o_extract)
        o_interface_handler.show()
        o_interface_handler.init_loading()


class InterfaceHandler(QMainWindow):

    basename_list_of_files_that_will_be_extracted = None
    list_of_files_that_will_be_extracted = None
    list_data = None
    full_raw_list_of_files = None
    extracting_value = 1

    histogram_level = None

    manual_interface_id = None

    max_statistics_error_value = -1
    list_statistics_error_value = None
    threshold_line = None

    def __init__(self, parent=None, o_extract=None):
        o_get = Get(parent=self)
        log_file_name = o_get.log_file_name()
        logging.basicConfig(filename=log_file_name,
                            filemode='w',
                            format='[%(levelname)s] - %(asctime)s - %(message)s',
                            level=logging.INFO)   # logging.INFO, logging.DEBUG
        logging.info("*** Starting new session ***")

        self.parent = parent
        self.o_extract = o_extract
        self.basename_list_of_files_that_will_be_extracted = \
            o_extract.basename_list_of_files_that_will_be_extracted
        self.list_of_files_that_will_be_extracted = o_extract.list_of_files_to_extract
        self.full_raw_list_of_files = o_extract.list_files
        self.full_base_list_of_files = [os.path.basename(_file) for _file in self.full_raw_list_of_files]
        self.extracting_value = self.o_extract.extracting_ui.value

        logging.info(f"number of files to extract: len(list_of_files_to_extract) = "
                     f" {len(self.list_of_files_that_will_be_extracted)}")
        logging.info(f"number of full list of files: len(full_raw_list_of_files) = {len(self.full_raw_list_of_files)}")

        super(InterfaceHandler, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_extract_evenly_spaced_files.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Extract Evenly Spaced Files")

        o_init = InterfaceInitialization(parent=self)
        o_init.all()

    def init_loading(self):
        self.ui.setEnabled(False)
        o_event = EventHandler(parent=self)
        o_event.load_files()
        o_event.select_first_file()
        o_statistics = Statistics(parent=self)
        o_statistics.update_statistics()
        o_statistics.plot_statistics()
        o_statistics.init_plot_statistics_threshold()
        self.ui.setEnabled(True)

    # event handler
    def image_selected_changed(self):
        o_event = EventHandler(parent=self)
        o_event.image_selected_changed()
        o_event.update_manual_ui()
        o_statistics = Statistics(parent=self)
        o_statistics.plot_statistics()
        self.check_previous_next_image_status()

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

    def list_files_right_click(self, point):
        o_event = EventHandler(parent=self)
        o_event.list_files_right_click()

    def statistics_max_threshold_moved(self):
        o_statistics = Statistics(parent=self)
        o_statistics.statistics_max_threshold_moved()

    def ok_clicked(self):
        if self.manual_interface_id:
            self.manual_interface_id.close()

        basename_list_of_files_that_will_be_extracted = self.basename_list_of_files_that_will_be_extracted
        self.o_extract.basename_list_of_files_that_will_be_extracted = basename_list_of_files_that_will_be_extracted
        self.close()

    def closeEvent(self, event=None):
        if not (self.manual_interface_id is None):
            self.manual_interface_id.close()
        self.close()
