from qtpy.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QLineEdit, QLabel
import os
import numpy as np
from PIL import Image

from __code import load_ui
from __code._utilities.table_handler import TableHandler


class AdvancedTableHandler(QMainWindow):

    list_formula_tableWidget_labels = []
    list_metatata_index_selected = []
    list_lineedit_ui_in_formula_tableWidget = []
    formula_table_cell_size = {'row': 50,
                               'column': 200}

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
        metadata_index_selected = self.ui.list_metadata_comboBox.currentIndex()
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

        self.add_metadata_to_formula_table(name=name, value=value)
        self.list_metatata_index_selected.append(metadata_index_selected)

        self.ui.statusbar.showMessage("")
        self.ui.statusbar.setStyleSheet("color: green")

        self.update_tableWidget()

    def coefficient_changed(self):
        self.update_tableWidget()

    def update_tableWidget(self):
        list_metadata_index_selected = self.list_metatata_index_selected
        list_files = self.parent.data_dict['file_name']
        list_lineedit_ui_in_formula_tableWidget = self.list_lineedit_ui_in_formula_tableWidget

        o_table = TableHandler(table_ui=self.ui.tableWidget)
        for _row, _file in enumerate(list_files):
            o_table.insert_item(row=_row, column=1, value="", editable=False)

            global_value = 0
            there_is_at_least_one_column = False
            for _column, _index_metadata in enumerate(list_metadata_index_selected):
                there_is_at_least_one_column = True
                key_selected = self.parent.list_metadata[_index_metadata]
                o_image = Image.open(_file)
                o_dict = dict(o_image.tag_v2)
                value = o_dict[float(key_selected)]

                if ":" in value:
                    name, value_str = value.split(":")
                    try:
                        value = np.float(value_str)
                    except ValueError:
                        self.ui.statusbar.showMessage("This metadata can not be used - not a float value!", 10000)
                        self.ui.statusbar.setStyleSheet("color: red")
                        return
                value = np.float(value)

                try:
                    coefficient = np.float(list_lineedit_ui_in_formula_tableWidget[_column].text())
                except ValueError:
                    self.ui.statusbar.showMessage(f"Coefficient in column {_column} is wrong!", 10000)
                    self.ui.statusbar.setStyleSheet("color: red")
                    return
                global_value += coefficient * value

            if there_is_at_least_one_column:
                o_table.insert_item(row=_row, column=1,value=global_value, editable=False)

        self.ui.statusbar.showMessage("Table refreshed with new formula!", 10000)
        self.ui.statusbar.setStyleSheet("color: green")

    def add_metadata_to_formula_table(self, name="", value=""):
        o_table = TableHandler(table_ui=self.ui.formula_tableWidget)
        nbr_column = o_table.column_count()

        o_table.insert_empty_column(column=nbr_column)

        widget = QWidget()
        hbox = QHBoxLayout()

        if nbr_column > 0:
            label = QLabel(f"+")
            hbox.addWidget(label)

        coeff_field = QLineEdit("1")
        coeff_field.blockSignals(True)
        coeff_field.returnPressed.connect(self.coefficient_changed)
        coeff_field.blockSignals(False)
        self.list_lineedit_ui_in_formula_tableWidget.append(coeff_field)
        label = QLabel(f"* {value}")
        hbox.addWidget(coeff_field)
        hbox.addWidget(label)
        widget.setLayout(hbox)
        o_table.insert_widget(row=0, column=nbr_column, widget=widget)

        column_width = np.ones((nbr_column + 1)) * self.formula_table_cell_size['column']
        o_table.set_column_width(column_width=column_width)

        self.list_formula_tableWidget_labels.append(name)
        o_table.set_column_names(self.list_formula_tableWidget_labels)
        self.ui.remove_metadata_button.setEnabled(True)

    def remove_metadata(self):
        o_table = TableHandler(table_ui=self.ui.formula_tableWidget)
        column_selected = o_table.get_column_selected()
        if column_selected == -1:
            return

        del(self.list_formula_tableWidget_labels[column_selected])
        del(self.list_metatata_index_selected[column_selected])
        del(self.list_lineedit_ui_in_formula_tableWidget[column_selected])
        o_table.remove_column(column=column_selected)
        self.update_tableWidget()
        if o_table.column_count() == 0:
            self.ui.remove_metadata_button.setEnabled(False)

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
        self.formula_table()

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

    def formula_table(self):
        o_table = TableHandler(table_ui=self.parent.ui.formula_tableWidget)
        o_table.set_row_height(row_height=[self.parent.formula_table_cell_size['row']])
