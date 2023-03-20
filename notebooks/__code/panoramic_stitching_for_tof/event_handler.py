import copy
import numpy as np

from __code._utilities.table_handler import TableHandler
from __code.panoramic_stitching_for_tof.get import Get


class TOFEventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def tab_changed(self, new_tab_index=-1):
        pass
        # if new_tab_index == 1:
        #     self.parent.coarse_alignment_table_combobox_changed()

    def update_working_images(self):
        if self.parent.ui.raw_image_radioButton.isChecked():
            coarse_images_dictionary = copy.deepcopy(self.parent.integrated_images)
        else:
            coarse_images_dictionary = copy.deepcopy(self.parent.best_contrast_images)

        self.parent.coarse_images_dictionary = coarse_images_dictionary

    def check_validate_coarse_alignment_button(self):
        # all files should have been checked once, and only once
        list_of_files = []

        nbr_row = self.parent.ui.coarse_alignment_tableWidget.rowCount()
        nbr_column = self.parent.ui.coarse_alignment_tableWidget.columnCount()

        o_table = TableHandler(table_ui=self.parent.ui.coarse_alignment_tableWidget)
        for _row in np.arange(nbr_row):
            for _col in np.arange(nbr_column):
                _widget = o_table.get_widget(row=_row, column=_col)
                folder_name = _widget.currentText()
                if not folder_name == "":
                    list_of_files.append(folder_name)

        list_folders = self.parent.list_folders
        error_message = ""
        if len(list_of_files) == 0:
            error_message = "Select the position of the images!"
            validate_button = False
        elif (len(list_of_files) == len(list_folders)) and (len(set(list_of_files)) == len(list_folders)):
            validate_button = True
        else:
            validate_button = False
            error_message = "Select each image only once!"

        self.parent.ui.validate_coarse_alignment_button.setEnabled(validate_button)
        self.parent.ui.validate_coarse_alignment_error.setText(error_message)
        self.parent.ui.validate_coarse_alignment_error.setVisible(not validate_button)

    def save_table_offset_of_this_cell(self, row=-1, column=-1, state=-1):
        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)

        folder_name = o_table.get_item_str_from_cell(row=row, column=0)
        offset_dictionary = self.parent.offset_dictionary
        if (column == 1) or (column == 2):
            offset_value = int(o_table.get_item_str_from_cell(row=row, column=column))

        if column == 1:
            offset_dictionary[folder_name]['xoffset'] = offset_value
        elif column == 2:
            offset_dictionary[folder_name]['yoffset'] = offset_value
        elif column == 3:
            is_visible = True if state == 2 else False
            offset_dictionary[folder_name]['visible'] = is_visible
        self.parent.offset_dictionary = offset_dictionary
