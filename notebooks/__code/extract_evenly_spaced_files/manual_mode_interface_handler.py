from qtpy.QtWidgets import QMainWindow
import os
import logging
import pyqtgraph as pg
from qtpy import QtGui
from qtpy.QtWidgets import QVBoxLayout
import numpy as np

from __code import load_ui
from __code._utilities.list_widget import ListWidget
from __code.extract_evenly_spaced_files.load import load_file
from __code.extract_evenly_spaced_files.get import Get


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
        # before
        self.ui.before_image_view = pg.ImageView(view=pg.PlotItem())
        self.ui.before_image_view.ui.menuBtn.hide()
        self.ui.before_image_view.ui.roiBtn.hide()
        vertical_layout1 = QVBoxLayout()
        vertical_layout1.addWidget(self.ui.before_image_view)
        self.ui.before_widget.setLayout(vertical_layout1)

        # after
        self.ui.after_image_view = pg.ImageView(view=pg.PlotItem())
        self.ui.after_image_view.ui.menuBtn.hide()
        self.ui.after_image_view.ui.roiBtn.hide()
        vertical_layout2 = QVBoxLayout()
        vertical_layout2.addWidget(self.ui.after_image_view)
        self.ui.after_widget.setLayout(vertical_layout2)

        self.update_current_image_name()
        self.update_replace_by_list()
        self.display_before_image()
        self.display_after_image()

    def update_current_image_name(self):
        o_list = ListWidget(ui=self.parent.ui.list_of_files_listWidget)
        index_file_selected = o_list.get_current_row()
        file_name = self.parent.basename_list_of_files_that_will_be_extracted[index_file_selected]
        self.ui.name_of_current_file.setText(file_name)

    def close_clicked(self):
        self.parent.manual_interface_id = None
        self.close()

    def closeEvent(self, eventhere=None):
        self.parent.manual_interface_id = None
        self.close()

    def validate_change(self):
        o_list = ListWidget(ui=self.parent.ui.list_of_files_listWidget)
        index_file_selected = o_list.get_current_row()
        new_file = self.ui.replace_by_comboBox.currentText()

        o_list = ListWidget(ui=self.parent.ui.list_of_files_listWidget)
        self.parent.basename_list_of_files_that_will_be_extracted[index_file_selected] = \
            os.path.basename(new_file)

        self.parent.ui.list_of_files_listWidget.clear()
        self.parent.ui.list_of_files_listWidget.addItems(self.parent.basename_list_of_files_that_will_be_extracted)

        self.parent.list_data[index_file_selected] = self.new_data
        self.parent.image_selected_changed()
        o_list.select_element(row=index_file_selected)

    def to_replace_by_changed(self, index):
        self.display_after_image()

    def display_before_image(self):
        o_list = ListWidget(ui=self.parent.ui.list_of_files_listWidget)
        index_file_selected = o_list.get_current_row()
        data = self.parent.list_data[index_file_selected]
        self.ui.before_image_view.setImage(np.transpose(data))

    def display_after_image(self):
        file = self.ui.replace_by_comboBox.currentText()
        data = load_file(file)
        self.ui.after_image_view.setImage(np.transpose(data))
        self.new_data = data

    def update_replace_by_list(self):
        o_list = ListWidget(ui=self.parent.ui.list_of_files_listWidget)
        full_list_of_files = self.parent.full_raw_list_of_files
        index_file_selected = o_list.get_current_row()
        extracting_value = self.parent.extracting_value

        logging.info(f"index_file_selected: {index_file_selected}")
        logging.info(f"extracting_value: {extracting_value}")

        self.ui.replace_by_comboBox.blockSignals(True)
        self.ui.replace_by_comboBox.clear()

        #index_file_selected_in_full_list = index_file_selected * extracting_value
        o_get = Get(parent=self.parent)
        base_file_name = self.parent.basename_list_of_files_that_will_be_extracted[index_file_selected]
        index_file_selected_in_full_list = o_get.index_of_file_selected_in_full_list(base_file_name)

        logging.info(f"base_file_name: {base_file_name}")
        logging.info(f"index_file_selected_in_full_list: {index_file_selected_in_full_list}")

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

        self.ui.replace_by_comboBox.blockSignals(False)
