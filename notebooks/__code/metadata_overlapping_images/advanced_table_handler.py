from qtpy.QtWidgets import QMainWindow
import os
import numpy as np

from __code import load_ui
from __code._utilities.table_handler import TableHandler


class AdvancedTableHandler(QMainWindow):

    def __init__(self, parent=None):
        self.parent = parent

        super(AdvancedTableHandler, self).__init__(parent)

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui', 'ui_metadata_overlapping_images_advanced_table.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)

        # initialization
        o_init = Initialization(parent=self,
                                top_parent=self.parent)
        o_init.all()

    def add_metadata(self):
        metadata_selected = self.ui.list_metadata_comboBox.currentText()
        metadata_code, metadata_value = metadata_selected.split("->")
        if ":" in metadata_value:
            name, value_str = metadata_value.split(":")
            try:
                value = np.float(value_str)
            except ValueError:
                self.ui.statusbar.showMessage("This metadata can not be used - not a float value!", 10000)
                self.ui.statusbar.setStyleSheet("color: red")
                return
        else:
            name = metadata_code
            value = metadata_value

        self.ui.statusbar.showMessage("")
        self.ui.statusbar.setStyleSheet("color: green")

    def remove_metadata(self):
        pass

    def cancel_clicked(self):
        self.close()

    def ok_clicked(self):
        pass


class Initialization:

    def __init__(self, parent=None, top_parent=None):
        self.parent = parent
        self.top_parent = top_parent

    def all(self):
        self.list_of_metadata()
        self.file_name_value_table()

    def list_of_metadata(self):
        list_of_metadata = self.top_parent.raw_list_metadata
        self.parent.ui.list_metadata_comboBox.addItems(list_of_metadata)

    def file_name_value_table(self):
        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        list_files_full_name = self.top_parent.data_dict['file_name']
        list_files_short_name = [os.path.basename(_file) for _file in list_files_full_name]

        o_table.insert_empty_column(0)
        o_table.insert_empty_column(1)
        o_table.set_column_names(column_names=['File Name', 'Value'])

        for _row, _file in enumerate(list_files_short_name):
            o_table.insert_empty_row(_row)
            o_table.insert_item(row=_row, column=0, value=_file, editable=False)

        o_table.set_column_width(column_width=[450])
