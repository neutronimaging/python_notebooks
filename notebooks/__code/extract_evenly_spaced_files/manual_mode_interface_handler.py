from qtpy.QtWidgets import QMainWindow
import os
import logging

from __code import load_ui
from __code._utilities.list_widget import ListWidget


class Interface:

    def __init__(self, parent=None):
        if parent.manual_interface_id is None:
            o_interface_handler = InterfaceHandler(parent=parent)
            o_interface_handler.show()
            o_interface_handler.init()
            parent.manual_interface_id = o_interface_handler
        else:
            parent.manual_interface_id.setFocus()


class InterfaceHandler(QMainWindow):

    def __init__(self, parent=None):
        logging.info("*** Starting Manual mode UI ***")
        self.parent = parent

        super(InterfaceHandler, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_extract_evenly_spaced_files_replace_with.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Manual Mode")

    def init(self):
        o_list = ListWidget(ui=self.parent.ui.list_of_files_listWidget)
        index_file_selected = o_list.get_current_row()
        file_name = self.parent.basename_list_of_files_that_will_be_extracted[index_file_selected]
        self.ui.name_of_current_file.setText(file_name)
        self.init_replace_by_list()

    def close_clicked(self):
        self.parent.manual_interface_id = None
        self.close()

    def to_replace_by_changed(self, index):
        pass

    def init_replace_by_list(self):
        o_list = ListWidget(ui=self.parent.ui.list_of_files_listWidget)
        full_list_of_files = self.parent.full_raw_list_of_files
        index_file_selected = o_list.get_current_row()
        extracting_value = self.parent.extracting_value
        self.ui.replace_by_comboBox.clear()

        if extracting_value == 1:
            self.parent.ui.replace_by_comboBox.setEnabled(False)
            self.parent.ui.or_label.setEnabled(False)
            return

        index_file_selected_in_full_list = index_file_selected * extracting_value
        # logging.info(f"-> index_file_selected_in_full_list: {index_file_selected_in_full_list}")
        if index_file_selected == 0:
            list_of_option_of_files_to_replace_with = \
            full_list_of_files[index_file_selected_in_full_list: index_file_selected_in_full_list + extracting_value]
        elif index_file_selected == (o_list.get_number_elements() - 1):
            list_of_option_of_files_to_replace_with = \
            full_list_of_files[index_file_selected_in_full_list - extracting_value:
                               index_file_selected_in_full_list]
        else:
            list_of_option_of_files_to_replace_with = []
            for _file in full_list_of_files[index_file_selected_in_full_list + 1 - extracting_value:
            index_file_selected_in_full_list]:
                    list_of_option_of_files_to_replace_with.append(_file)

            for _file in full_list_of_files[index_file_selected_in_full_list: index_file_selected_in_full_list +
                                                                     extracting_value]:
                    list_of_option_of_files_to_replace_with.append(_file)

        self.ui.replace_by_comboBox.addItems(list_of_option_of_files_to_replace_with)

        # select current file as default (mid point in the list)
        nbr_option = len(list_of_option_of_files_to_replace_with)
        mid_point = int(nbr_option/2)
        self.ui.replace_by_comboBox.setCurrentIndex(mid_point)
