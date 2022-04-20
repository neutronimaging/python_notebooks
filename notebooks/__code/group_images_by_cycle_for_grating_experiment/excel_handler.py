import pandas as pd
from qtpy.QtWidgets import QMainWindow, QLabel, QPushButton, QHBoxLayout, QWidget, QSpinBox
from qtpy.QtWidgets import QTableWidgetItem, QComboBox
from qtpy import QtCore
from IPython.core.display import display
from IPython.core.display import HTML
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

        df = pd.read_excel(excel_file, sheet_name="Tabelle1", header=0)
        self.pandas_object = df

        nbr_excel_row = len(df)
        nbr_notebook_row = len(self.parent.first_last_run_of_each_group_dictionary.keys())

        if nbr_excel_row != nbr_notebook_row:
            display(HTML("<font color='red'>Number of rows in Excel document selected and number of group <b>DO NOT "
                         "MATCH!</b></font>"))
            display(HTML("<font color='blue'><b>SOLUTION</b>: create a new Excel document!</font>"))

        else:
            o_interface = Interface(grand_parent=self.parent,
                                    excel_file=excel_file,
                                    first_last_run_of_each_group_dictionary=self.parent.first_last_run_of_each_group_dictionary)
            o_interface.show()

    def new_excel(self):
        self.parent.excel_info_widget.value = f"<b>Working with new excel file!"

        o_interface = Interface(grand_parent=self.parent,
                                first_last_run_of_each_group_dictionary=self.parent.first_last_run_of_each_group_dictionary)
        o_interface.show()


class Interface(QMainWindow):

    pandas_object = None  # pandas excel object
    excel_config = None

    def __init__(self, parent=None, grand_parent=None, excel_file=None, first_last_run_of_each_group_dictionary=None):

        display(format_html_message(pre_message="Check UI that popped up \
                    (maybe hidden behind this browser!)",
                                    spacer=""))

        super(Interface, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_grating_excel_editor.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Excel Editor")

        # dictionary giving first and last run for each group (row)
        self.first_last_run_of_each_group_dictionary = first_last_run_of_each_group_dictionary

        self.load_config()
        self.set_columns_width()

        self.load_excel(excel_file=excel_file)
        self.fill_table()

        # make sure the size of excel and group from notebook match
        pandas_object = self.pandas_object
        if pandas_object is None:
            show_status_message(parent=self,
                                message=f"Error loading excel!",
                                status=StatusMessageStatus.error,
                                duration_s=20)
            return

        list_columns = len(pandas_object)
        nbr_group = len(self.first_last_run_of_each_group_dictionary.keys())
        if list_columns != nbr_group:
            show_status_message(parent=self,
                                message=f"Excel loaded and number of new entries do not match!",
                                status=StatusMessageStatus.warning,
                                duration_s=20)

    def load_config(self):
        config_file = os.path.join(os.path.dirname(__file__), 'excel_config.json')
        with open(config_file) as json_file:
            self.excel_config = json.load(json_file)

    def set_columns_width(self):
        columns_width = [int(value) for value in np.ones(28) * 100]

        list_very_wide_columns = [0, 1, 2, 3, 4, 5, 23]
        for index in list_very_wide_columns:
            columns_width[index] = 400

        list_wide_columns = [10, 24]
        for index in list_wide_columns:
            columns_width[index] = 150

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

        fill_sample_columns_with_pandas = False
        fill_ob_columns_with_pandas = False

        if self.ui.sample_radioButton.isChecked():
            self.fill_sample_columns_with_data_from_notebook()
            fill_ob_columns_with_pandas = True

        else:
            self.fill_ob_columns_with_data_from_notebook()
            fill_sample_columns_with_pandas = True

        pandas_entry_for_first_row = pandas_object.iloc[0]

        nbr_rows = len(pandas_object)
        for _row in np.arange(nbr_rows):
            o_table.insert_empty_row(_row)

            pandas_entry_for_this_row = pandas_object.iloc[_row]

            if fill_sample_columns_with_pandas:

                # first_sample_file
                column_index = 0
                start_sample_file = pandas_entry_for_this_row[column_index]
                start_sample_file_label = QLabel(start_sample_file)
                start_sample_file_button = QPushButton("Browse")
                start_sample_file_layout = QHBoxLayout()
                start_sample_file_layout.addWidget(start_sample_file_label)
                start_sample_file_layout.addWidget(start_sample_file_button)
                start_sample_file_widget = QWidget()
                start_sample_file_widget.setLayout(start_sample_file_layout)
                o_table.insert_widget(row=_row, column=column_index, widget=start_sample_file_widget)

                # last_sample_file
                column_index = 1
                end_sample_file = pandas_entry_for_this_row[column_index]
                end_sample_file_label = QLabel(end_sample_file)
                end_sample_file_button = QPushButton("Browse")
                end_sample_file_layout = QHBoxLayout()
                end_sample_file_layout.addWidget(end_sample_file_label)
                end_sample_file_layout.addWidget(end_sample_file_button)
                end_sample_file_widget = QWidget()
                end_sample_file_widget.setLayout(end_sample_file_layout)
                o_table.insert_widget(row=_row, column=column_index, widget=end_sample_file_widget)

            if fill_ob_columns_with_pandas:

                # first_ob_file
                column_index = 2
                start_ob_file = pandas_entry_for_this_row[column_index]
                start_ob_file_label = QLabel(start_ob_file)
                start_ob_file_button = QPushButton("Browse")
                start_ob_file_layout = QHBoxLayout()
                start_ob_file_layout.addWidget(start_ob_file_label)
                start_ob_file_layout.addWidget(start_ob_file_button)
                start_ob_file_widget = QWidget()
                start_ob_file_widget.setLayout(start_ob_file_layout)
                o_table.insert_widget(row=_row, column=column_index, widget=start_ob_file_widget)

                # last_ob_file
                column_index = 3
                end_ob_file = pandas_entry_for_this_row[column_index]
                end_ob_file_label = QLabel(end_ob_file)
                end_ob_file_button = QPushButton("Browse")
                end_ob_file_layout = QHBoxLayout()
                end_ob_file_layout.addWidget(end_ob_file_label)
                end_ob_file_layout.addWidget(end_ob_file_button)
                end_ob_file_widget = QWidget()
                end_ob_file_widget.setLayout(end_ob_file_layout)
                o_table.insert_widget(row=_row, column=column_index, widget=end_ob_file_widget)

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
            end_dc_file = pandas_entry_for_first_row[column_index]
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
            period_value = pandas_entry_for_first_row[column_index]
            period_widget.setMinimum(1)
            period_widget.setMaximum(10)
            period_widget.setValue(period_value)
            o_table.insert_widget(row=_row, column=column_index, widget=period_widget)

            # images per step
            column_index = 7
            images_per_step = QSpinBox()
            images_per_step_value = pandas_entry_for_first_row[column_index]
            images_per_step.setMinimum(1)
            images_per_step.setMaximum(10)
            images_per_step.setValue(images_per_step_value)
            o_table.insert_widget(row=_row, column=column_index, widget=images_per_step)

            # rotation  # not editable
            column_index = 8
            rotation_value = str(pandas_entry_for_first_row[column_index])
            item = QTableWidgetItem(rotation_value)
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            o_table.insert_item(row=_row, column=column_index, item=item)

            # fit procedure
            column_index = 9
            fit_procedure = QComboBox()
            fit_procedure_value = pandas_entry_for_first_row[column_index]
            list_procedure = self.excel_config['list_fit_procedure']
            fit_procedure.addItems(list_procedure)
            index = list_procedure.index(fit_procedure_value)
            fit_procedure.setCurrentIndex(index)
            o_table.insert_widget(row=_row, column=column_index, widget=fit_procedure)

            # roi
            column_index = 10
            roi_value = pandas_entry_for_first_row[column_index]
            roi_item = QTableWidgetItem(roi_value)
            o_table.insert_item(row=_row, column=column_index, item=roi_item)

            # gamma_filter_data/ob
            column_index = 11
            gamma_filter_value = str(pandas_entry_for_first_row[column_index])
            values = ['yes', 'no']
            gamma_filter_ui = QComboBox()
            gamma_filter_ui.addItems(values)
            gamma_filter_ui.setCurrentText(gamma_filter_value)
            o_table.insert_widget(row=_row, column=column_index, widget=gamma_filter_ui)

            # data 3x3
            column_index = 12
            data_threshold_3x3_value = str(pandas_entry_for_first_row[column_index])
            item_data_3x3 = QTableWidgetItem(data_threshold_3x3_value)
            o_table.insert_item(row=_row, column=column_index, item=item_data_3x3)

            # data 5x5
            column_index = 13
            data_threshold_5x5_value = str(pandas_entry_for_first_row[column_index])
            item_data_5x5 = QTableWidgetItem(data_threshold_5x5_value)
            o_table.insert_item(row=_row, column=column_index, item=item_data_5x5)

            # data 7x7
            column_index = 14
            data_threshold_7x7_value = str(pandas_entry_for_first_row[column_index])
            item_data_7x7 = QTableWidgetItem(data_threshold_7x7_value)
            o_table.insert_item(row=_row, column=column_index, item=item_data_7x7)

            # data sigma log
            column_index = 15
            data_sigma_log_value = str(pandas_entry_for_first_row[column_index])
            item_data_sigma = QTableWidgetItem(data_sigma_log_value)
            o_table.insert_item(row=_row, column=column_index, item=item_data_sigma)

            # gamma_filter_dc
            column_index = 16
            gamma_filter_value = pandas_entry_for_first_row[column_index]
            values = ['yes', 'no']
            gamma_filter_dc_ui = QComboBox()
            gamma_filter_dc_ui.addItems(values)
            gamma_filter_dc_ui.setCurrentText(gamma_filter_value)
            o_table.insert_widget(row=_row, column=column_index, widget=gamma_filter_dc_ui)

            # dc 3x3
            column_index = 17
            dc_threshold_3x3_value = str(pandas_entry_for_first_row[column_index])
            item_dc_3x3 = QTableWidgetItem(dc_threshold_3x3_value)
            o_table.insert_item(row=_row, column=column_index, item=item_dc_3x3)

            # dc 5x5
            column_index = 18
            dc_threshold_5x5_value = str(pandas_entry_for_first_row[column_index])
            item_dc_5x5 = QTableWidgetItem(dc_threshold_5x5_value)
            o_table.insert_item(row=_row, column=column_index, item=item_dc_5x5)

            # dc 7x7
            column_index = 19
            dc_threshold_7x7_value = str(pandas_entry_for_first_row[column_index])
            item_dc_7x7 = QTableWidgetItem(dc_threshold_7x7_value)
            o_table.insert_item(row=_row, column=column_index, item=item_dc_7x7)

            # dc log
            column_index = 20
            dc_sigma_log_value = str(pandas_entry_for_this_row[column_index])
            item_dc_sigma = QTableWidgetItem(dc_sigma_log_value)
            o_table.insert_item(row=_row, column=column_index, item=item_dc_sigma)

            # dc_outlier_removal
            column_index = 21
            dc_outlier_value = pandas_entry_for_first_row[column_index]
            values = ['yes', 'no']
            dc_outlier_ui = QComboBox()
            dc_outlier_ui.addItems(values)
            dc_outlier_ui.setCurrentText(dc_outlier_value)
            o_table.insert_widget(row=_row, column=column_index, widget=dc_outlier_ui)

            # dc_outlier_value
            column_index = 22
            dc_outlier_value = str(pandas_entry_for_first_row[column_index])
            dc_outlier = QTableWidgetItem(dc_outlier_value)
            o_table.insert_item(row=_row, column=column_index, item=dc_outlier)

            # result_directory
            column_index = 23
            result_directory = pandas_entry_for_first_row[column_index]
            result_directory_label = QLabel(result_directory)
            result_directory_button = QPushButton("Browse")
            result_directory_layout = QHBoxLayout()
            result_directory_layout.addWidget(result_directory_label)
            result_directory_layout.addWidget(result_directory_button)
            result_directory_widget = QWidget()
            result_directory_widget.setLayout(result_directory_layout)
            o_table.insert_widget(row=_row, column=column_index, widget=result_directory_widget)

            # file_id
            column_index = 24
            file_id_value = pandas_entry_for_this_row[column_index]
            file_id = QTableWidgetItem(file_id_value)
            o_table.insert_item(row=_row, column=column_index, item=file_id)

            # sample information
            # NOT USED

            # used_environment
            # NOT USED

            # osc_pixel
            # NOT USED


        row_height = [int(value) for value in np.ones(nbr_rows) * ROW_HEIGHT]
        o_table.set_row_height(row_height=row_height)

        o_table.set_column_width(column_width=self.columns_width)

    def fill_sample_columns_with_data_from_notebook(self):
        first_last_run_of_each_group_dictionary = self.first_last_run_of_each_group_dictionary
        list_sample_first_run = []
        list_sample_last_run = []
        for _group in first_last_run_of_each_group_dictionary.keys():
            list_sample_first_run.append(first_last_run_of_each_group_dictionary[_group]['first'])
            list_sample_last_run.append(first_last_run_of_each_group_dictionary[_group]['last'])

        pandas_object = self.pandas_object
        nbr_row = len(pandas_object)
        list_ob_first_run = []
        list_ob_last_run = []
        for _row in np.arange(nbr_row):
            list_ob_first_run.append(pandas_object.iloc[_row][2])
            list_ob_last_run.append(pandas_object.iloc[_row][3])

        self.refresh_sample_ob_columns(list_sample_first_run=list_sample_first_run,
                                       list_sample_last_run=list_sample_last_run,
                                       list_ob_first_run=list_ob_first_run,
                                       list_ob_last_run=list_ob_last_run,
                                       )

    def fill_ob_columns_with_data_from_notebook(self):
        first_last_run_of_each_group_dictionary = self.first_last_run_of_each_group_dictionary
        list_sample_first_run = []
        list_sample_last_run = []
        pandas_object = self.pandas_object
        nbr_row = len(pandas_object)
        for _row in np.arange(nbr_row):
            list_sample_first_run.append(pandas_object.iloc[_row][0])
            list_sample_last_run.append(pandas_object.iloc[_row][1])

        list_ob_first_run = []
        list_ob_last_run = []
        for _group in first_last_run_of_each_group_dictionary.keys():
            list_ob_first_run.append(first_last_run_of_each_group_dictionary[_group]['first'])
            list_ob_last_run.append(first_last_run_of_each_group_dictionary[_group]['last'])

        self.refresh_sample_ob_columns(list_sample_first_run=list_sample_first_run,
                                       list_sample_last_run=list_sample_last_run,
                                       list_ob_first_run=list_ob_first_run,
                                       list_ob_last_run=list_ob_last_run,
                                       )

    def refresh_sample_ob_columns(self, list_sample_first_run=None, list_sample_last_run=None,
                                  list_ob_first_run=None, list_ob_last_run=None):
        pass



    def cancel_button_pushed(self):
        self.close()

    def save_as_button_pushed(self):
        print("save as")
