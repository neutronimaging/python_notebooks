import pandas as pd
from qtpy.QtWidgets import QMainWindow, QLabel, QPushButton, QHBoxLayout, QWidget, QSpinBox
from qtpy.QtWidgets import QTableWidgetItem, QComboBox
from qtpy import QtCore
from IPython.core.display import display
import os
import numpy as np
import json

from __code._utilities.string import format_html_message
from __code import load_ui
from __code._utilities.status_message import StatusMessageStatus, show_status_message
from __code._utilities.table_handler import TableHandler

ROW_HEIGHT = 40


class ExcelHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def load_excel(self, excel_file=None):
        if excel_file is None:
            return

        self.parent.excel_info_widget.value = f"<b>Loaded excel file</b>: {excel_file}!"

        o_interface = Interface(grand_parent=self.parent, excel_file=excel_file)
        o_interface.show()

    def new_excel(self):
        self.parent.excel_info_widget.value = f"<b>Working with new excel file!"

        o_interface = Interface(grand_parent=self.parent)
        o_interface.show()


class Interface(QMainWindow):

    pandas_object = None  # pandas excel object
    excel_config = None

    def __init__(self, parent=None, grand_parent=None, excel_file=None):

        display(format_html_message(pre_message="Check UI that popped up \
                    (maybe hidden behind this browser!)",
                                    spacer=""))

        super(Interface, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_grating_excel_editor.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Excel Editor")

        self.load_config()
        self.set_columns_width()

        self.load_excel(excel_file=excel_file)
        self.fill_table()

    def load_config(self):
        config_file = os.path.join(os.path.dirname(__file__), 'excel_config.json')
        with open(config_file) as json_file:
            self.excel_config = json.load(json_file)

    def set_columns_width(self):
        columns_width = [int(value) for value in np.ones(28) * 100]
        for index in np.arange(0, 6):
            columns_width[index] = 400
        self.columns_width = columns_width

    def load_excel(self, excel_file=None):
        if excel_file:
            df = pd.read_excel(excel_file, sheet_name="Tabelle1", header=0)
            self.pandas_object = df
            show_status_message(parent=self,
                                message=f"Loaded excel file {excel_file}!",
                                status=StatusMessageStatus.ready,
                                duration_s=10)
        else:
            df = self.initialize_new_excel()
            self.pandas_object = df
            show_status_message(parent=self,
                                message=f"Created a new Excel file!",
                                status=StatusMessageStatus.ready,
                                duration_s=10)

    def initialize_new_excel(self):
        pass

    def fill_table(self):
        pandas_object = self.pandas_object
        if pandas_object is None:
            return

        list_columns = pandas_object.columns
        o_table = TableHandler(table_ui=self.ui.tableWidget)

        nbr_columns = len(list_columns)
        for _col_index in np.arange(nbr_columns):
            o_table.insert_column(_col_index)
        o_table.set_column_names(list_columns)

        nbr_rows = len(pandas_object)
        for _row in np.arange(nbr_rows):
            o_table.insert_empty_row(_row)

            pandas_entry_for_this_row = pandas_object.iloc[_row]

            # first_dc_file
            column_index = 4
            start_dc_file = pandas_entry_for_this_row[column_index]
            start_dc_file_label = QLabel(start_dc_file)
            start_dc_file_button = QPushButton("Browse")
            start_dc_file_layout = QHBoxLayout()
            start_dc_file_layout.addWidget(start_dc_file_label)
            start_dc_file_layout.addWidget(start_dc_file_button)
            start_dc_file_widget = QWidget()
            start_dc_file_widget.setLayout(start_dc_file_layout)
            o_table.insert_widget(row=_row, column=column_index, widget=start_dc_file_widget)
            
            # last_dc_file
            column_index = 5
            end_dc_file = pandas_entry_for_this_row[column_index]
            end_dc_file_label = QLabel(end_dc_file)
            end_dc_file_button = QPushButton("Browse")
            end_dc_file_layout = QHBoxLayout()
            end_dc_file_layout.addWidget(end_dc_file_label)
            end_dc_file_layout.addWidget(end_dc_file_button)
            end_dc_file_widget = QWidget()
            end_dc_file_widget.setLayout(end_dc_file_layout)
            o_table.insert_widget(row=_row, column=column_index, widget=end_dc_file_widget)

            # period
            column_index = 6
            period_widget = QSpinBox()
            period_value = pandas_entry_for_this_row[column_index]
            period_widget.setMinimum(1)
            period_widget.setMaximum(10)
            period_widget.setValue(period_value)
            o_table.insert_widget(row=_row, column=column_index, widget=period_widget)

            # images per step
            column_index = 7
            images_per_step = QSpinBox()
            images_per_step_value = pandas_entry_for_this_row[column_index]
            images_per_step.setMinimum(1)
            images_per_step.setMaximum(10)
            images_per_step.setValue(images_per_step_value)
            o_table.insert_widget(row=_row, column=column_index, widget=images_per_step)

            # rotation  # not editable
            column_index = 8
            rotation_value = str(pandas_entry_for_this_row[column_index])
            item = QTableWidgetItem(rotation_value)
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            o_table.insert_item(row=_row, column=column_index, item=item)

            # fit procedure
            column_index = 9
            fit_procedure = QComboBox()
            fit_procedure_value = pandas_entry_for_this_row[column_index]
            list_procedure = self.excel_config['list_fit_procedure']
            fit_procedure.addItems(list_procedure)
            index = list_procedure.index(fit_procedure_value)
            fit_procedure.setCurrentIndex(index)
            o_table.insert_widget(row=_row, column=column_index, widget=fit_procedure)

        self.fill_sample_columns()
        self.fill_ob_columns()

        row_height = [int(value) for value in np.ones(nbr_rows) * ROW_HEIGHT]
        o_table.set_row_height(row_height=row_height)

        o_table.set_column_width(column_width=self.columns_width)

    def fill_sample_columns(self):
        if self.ui.sample_radioButton.isChecked():
            print("ob: fill with data from notebook")
        else:
            print("ob: fill with data from pandas object")

    def fill_ob_columns(self):
        if self.ui.ob_radioButton.isChecked():
            print("ob: fill with data from notebook")
        else:
            print("ob: fill with data from pandas object")

    def cancel_button_pushed(self):
        self.close()

    def save_as_button_pushed(self):
        print("save as")
