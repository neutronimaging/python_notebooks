import pandas as pd
from qtpy.QtWidgets import QMainWindow, QSpinBox, QFileDialog, QMenu
from qtpy.QtWidgets import QTableWidgetItem, QComboBox
from qtpy import QtCore, QtGui
from IPython.core.display import display
from IPython.core.display import HTML
import os
import numpy as np
import re
import json
from collections import OrderedDict

from __code._utilities.string import format_html_message
from __code import load_ui
from __code._utilities.status_message import StatusMessageStatus, show_status_message
from __code.group_images_by_cycle_for_grating_experiment.excel_table_handler import ExcelTableHandler as TableHandler
from __code.group_images_by_cycle_for_grating_experiment import list_fit_procedure

ROW_HEIGHT = 40


class ExcelHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def load_excel(self, excel_file=None):
        if excel_file is None:
            return

        self.parent.excel_info_widget.value = f"<b>Loaded excel file</b>: {excel_file}!"


        df = pd.read_excel(excel_file, sheet_name="Tabelle1", header=0)

        nbr_excel_row = len(df)
        nbr_notebook_row = len(self.parent.first_last_run_of_each_group_dictionary.keys())

        if nbr_excel_row != nbr_notebook_row:
            display(HTML("<font color='red'>Number of rows in Excel document selected and number of group <b>DO NOT "
                         "MATCH!</b></font>"))
            display(HTML("<font color='blue'><b>SOLUTION</b>: create a new Excel document!</font>"))

        else:
            data_type_to_populate_with_notebook_data = self.parent.sample_or_ob_radio_buttons.value
            df = self._populate_pandas_object(
                    df=df,
                    data_type_to_populate_with_notebook_data=data_type_to_populate_with_notebook_data)

            o_interface = Interface(grand_parent=self.parent,
                                    excel_file=excel_file,
                                    pandas_object=df,
                                    data_type_to_populate_with_notebook_data=data_type_to_populate_with_notebook_data,
                                    first_last_run_of_each_group_dictionary=self.parent.first_last_run_of_each_group_dictionary)
            o_interface.show()

    def get_excel_config(self):
        config_file = os.path.join(os.path.dirname(__file__), 'excel_config.json')
        with open(config_file) as json_file:
            return json.load(json_file)

    def _populate_pandas_object(self, df=None, data_type_to_populate_with_notebook_data='sample'):
        first_last_run_of_each_group_dictionary = self.parent.first_last_run_of_each_group_dictionary
        if data_type_to_populate_with_notebook_data == 'sample':

            for _row_index, _key in enumerate(first_last_run_of_each_group_dictionary.keys()):
                df.iloc[_row_index][0] = first_last_run_of_each_group_dictionary[_key]['first']
                df.iloc[_row_index][1] = first_last_run_of_each_group_dictionary[_key]['last']

        else:  # ob

            for _row_index, _key in enumerate(first_last_run_of_each_group_dictionary.keys()):
                df.iloc[_row_index][2] = first_last_run_of_each_group_dictionary[_key]['first']
                df.iloc[_row_index][3] = first_last_run_of_each_group_dictionary[_key]['last']

        return df

    def _create_pandas_object(self, data_type_to_populate_with_notebook_data='sample'):
        first_last_run_of_each_group_dictionary = self.parent.first_last_run_of_each_group_dictionary
        excel_config = self.get_excel_config()

        df_dict = OrderedDict()
        if data_type_to_populate_with_notebook_data == 'sample':

            for _row_index, _key in enumerate(first_last_run_of_each_group_dictionary.keys()):

                if _row_index == 0:
                    df_dict["first_data_file"] = [first_last_run_of_each_group_dictionary[_key]['first']]
                    df_dict["last_data_file"] = [first_last_run_of_each_group_dictionary[_key]['last']]
                else:
                    df_dict["first_data_file"].append(first_last_run_of_each_group_dictionary[_key]['first'])
                    df_dict["last_data_file"].append(first_last_run_of_each_group_dictionary[_key]['last'])

            nbr_row = len(first_last_run_of_each_group_dictionary.keys())
            df_dict["first_ob_file"] = ["None" for _ in np.arange(nbr_row)]
            df_dict["last_ob_file"] = ["None" for _ in np.arange(nbr_row)]

        else:  # ob

            for _row_index, _key in enumerate(first_last_run_of_each_group_dictionary.keys()):

                nbr_row = len(first_last_run_of_each_group_dictionary.keys())
                df_dict["first_sample_file"] = ["None" for _ in np.arange(nbr_row)]
                df_dict["last_sample_file"] = ["None" for _ in np.arange(nbr_row)]

                if _row_index == 0:
                    df_dict["first_ob_file"] = [first_last_run_of_each_group_dictionary[_key]['first']]
                    df_dict["last_ob_file"] = [first_last_run_of_each_group_dictionary[_key]['last']]
                else:
                    df_dict["first_ob_file"].append(first_last_run_of_each_group_dictionary[_key]['first'])
                    df_dict["last_ob_file"].append(first_last_run_of_each_group_dictionary[_key]['last'])

        df_dict["first_dc_file"] = ["None" for _ in np.arange(nbr_row)]
        df_dict["last_dc_file"] = ["None" for _ in np.arange(nbr_row)]

        list_key = list(excel_config.keys())
        list_key.remove("first_data_file")
        list_key.remove("last_data_file")
        list_key.remove("first_ob_file")
        list_key.remove("last_ob_file")
        for _key in list_key:
            df_dict[_key] = [excel_config[_key] for _ in np.arange(nbr_row)]

        df = pd.DataFrame(data=df_dict)
        return df

    def new_excel(self):
        self.parent.excel_info_widget.value = f"<b>Working with new excel file!"
        data_type_to_populate_with_notebook_data = self.parent.sample_or_ob_radio_buttons.value

        pandas_object = self._create_pandas_object(data_type_to_populate_with_notebook_data=data_type_to_populate_with_notebook_data)

        o_interface = Interface(grand_parent=self.parent,
                                pandas_object=pandas_object,
                                data_type_to_populate_with_notebook_data=data_type_to_populate_with_notebook_data,
                                first_last_run_of_each_group_dictionary=self.parent.first_last_run_of_each_group_dictionary)
        o_interface.show()


class Interface(QMainWindow):
    pandas_object = None  # pandas excel object
    excel_config = None

    def __init__(self, parent=None, grand_parent=None, excel_file=None,
                 first_last_run_of_each_group_dictionary=None,
                 data_type_to_populate_with_notebook_data='sample',
                 pandas_object=None):

        display(format_html_message(pre_message="Check UI that popped up \
                    (maybe hidden behind this browser!)",
                                    spacer=""))
        self.grand_parent = grand_parent
        self.data_type_to_populate_with_notebook_data = data_type_to_populate_with_notebook_data

        self.pandas_object = pandas_object
        super(Interface, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_grating_excel_editor.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Excel Editor")
        self.excel_file = excel_file

        # dictionary giving first and last run for each group (row)
        self.first_last_run_of_each_group_dictionary = first_last_run_of_each_group_dictionary

        self.init_statusbar_message()

        self.load_config()
        self.set_columns_width()

        self.fill_table()
        self.check_table_content_pushed()

    def check_table_content_pushed(self):
        """this is where we will check to make sure the format of all the cells is right and they are
        no missing fields"""
        o_table = TableHandler(table_ui=self.ui.tableWidget)
        nbr_rows = o_table.row_count()

        color_error = QtGui.QColor(255, 0, 0)
        color_ok = QtGui.QColor(255, 255, 255)

        self.at_least_one_error_found = False

        def is_string_a_float(string):
            try:
                float(string)
                return True
            except ValueError:
                return False

        def is_string_an_integer(string):
            try:
                int(string)
                return True
            except ValueError:
                return False

        def set_color_for_float_field(string, row, column):
            if is_string_a_float(string):
                color = color_ok
            else:
                color = color_error
                self.at_least_one_error_found = True
            o_table.set_background_color(row, column, color)

        def set_color_for_int_field(string, row, column):
            if is_string_an_integer(string):
                color = color_ok
            else:
                color = color_error
                self.at_least_one_error_found = True
            o_table.set_background_color(row, column, color)

        def is_string_undefined_or_empty(string):
            if string.lower() in ["none", "nan", ""]:
                return True
            return False

        def set_color_for_that_mandatory_field(string, row, column):
            if is_string_undefined_or_empty(string):
                color = color_error
                self.at_least_one_error_found = True
            else:
                color = color_ok
            o_table.set_background_color(row, column, color)

        def is_roi_correct_format(roi):
            """check if roi has the format [##,##,##,##] where ## are integers"""
            roi = roi.strip()
            print(f"roi: {roi}")
            result = re.search("\[\s*(\d*)\s*,\s*(\d*)\s*,\s*(\d*)\s*,\s*(\d*)\s*\]", roi)
            if len(result.groups()) != 4:
                return False
            try:
                int(result.groups()[0])
                int(result.groups()[1])
                int(result.groups()[2])
                int(result.groups()[3])
            except ValueError:
                return False
            return True

        def set_color_for_roi(roi, row, column):
            if is_roi_correct_format(roi):
                color = color_ok
            else:
                color = color_error
                self.at_least_one_error_found = True
            o_table.set_background_color(row, column, color)

        for _row in np.arange(nbr_rows):
            o_table.set_row(row=_row)

            first_data_file = o_table.get_first_data_file()
            set_color_for_that_mandatory_field(first_data_file, _row, 0)

            last_data_file = o_table.get_last_data_file()
            set_color_for_that_mandatory_field(last_data_file, _row, 1)

            first_ob_file = o_table.get_first_ob_file()
            set_color_for_that_mandatory_field(first_ob_file, _row, 2)

            last_ob_file = o_table.get_last_ob_file()
            set_color_for_that_mandatory_field(last_ob_file, _row, 3)

            first_dc_file = o_table.get_first_dc_file()
            set_color_for_that_mandatory_field(first_dc_file, _row, 4)

            last_dc_file = o_table.get_last_dc_file()
            set_color_for_that_mandatory_field(last_dc_file, _row, 5)

            rotation = o_table.get_rotation()
            set_color_for_int_field(rotation, _row, 8)

            roi = o_table.get_roi()
            set_color_for_roi(roi, _row, 10)

            data_threshold_3x3 = o_table.get_data_threshold_3x3()
            set_color_for_int_field(data_threshold_3x3, _row, 12)

            data_threshold_5x5 = o_table.get_data_threshold_5x5()
            set_color_for_int_field(data_threshold_5x5, _row, 13)

            data_threshold_7x7 = o_table.get_data_threshold_7x7()
            set_color_for_int_field(data_threshold_7x7, _row, 14)

            data_sigma_log = o_table.get_data_sigma_log()
            set_color_for_float_field(data_sigma_log, _row, 15)

            dc_threshold_3x3 = o_table.get_dc_threshold_3x3()
            set_color_for_int_field(dc_threshold_3x3, _row, 17)

            dc_threshold_5x5 = o_table.get_dc_threshold_5x5()
            set_color_for_int_field(dc_threshold_5x5, _row, 18)

            dc_threshold_7x7 = o_table.get_dc_threshold_7x7()
            set_color_for_int_field(dc_threshold_7x7, _row, 19)

            dc_sigma_log = o_table.get_dc_log()
            set_color_for_float_field(dc_sigma_log, _row, 20)

            dc_outlier_value = o_table.get_dc_outlier_value()
            set_color_for_float_field(dc_outlier_value, _row, 22)

            result_directory = o_table.get_result_directory()
            set_color_for_that_mandatory_field(result_directory, _row, 23)

            file_id = o_table.get_file_id()
            set_color_for_that_mandatory_field(file_id, _row, 24)

        if self.at_least_one_error_found:
            show_status_message(parent=self,
                                message=f"At least one issue found in table! Angel will not be able to execute this "
                                        f"excel!",
                                status=StatusMessageStatus.error,
                                duration_s=15)

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

    def init_statusbar_message(self):
        if self.excel_file:
            show_status_message(parent=self,
                                message=f"Loaded excel file {self.excel_file}!",
                                status=StatusMessageStatus.ready,
                                duration_s=10)
        else:
            show_status_message(parent=self,
                                message="Created a new Excel file!",
                                status=StatusMessageStatus.ready,
                                duration_s=10)

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

        pandas_entry_for_first_row = pandas_object.iloc[0]

        nbr_rows = len(pandas_object)
        for _row in np.arange(nbr_rows):
            o_table.insert_empty_row(_row)

            pandas_entry_for_this_row = pandas_object.iloc[_row]

            # first_sample_file
            column_index = 0
            start_sample_file = str(pandas_entry_for_this_row[column_index])
            _item = QTableWidgetItem(start_sample_file)
            o_table.insert_item(row=_row, column=column_index, item=_item)

            # last_sample_file
            column_index = 1
            end_sample_file = str(pandas_entry_for_this_row[column_index])
            _item = QTableWidgetItem(end_sample_file)
            o_table.insert_item(row=_row, column=column_index, item=_item)

            # first_ob_file
            column_index = 2
            start_ob_file = str(pandas_entry_for_this_row[column_index])
            _item = QTableWidgetItem(start_ob_file)
            o_table.insert_item(row=_row, column=column_index, item=_item)

            # last_ob_file
            column_index = 3
            end_ob_file = str(pandas_entry_for_this_row[column_index])
            _item = QTableWidgetItem(end_ob_file)
            o_table.insert_item(row=_row, column=column_index, item=_item)

            # first_dc_file
            column_index = 4
            start_dc_file = str(pandas_entry_for_this_row[column_index])
            _item = QTableWidgetItem(start_dc_file)
            o_table.insert_item(row=_row, column=column_index, item=_item)

            # last_dc_file
            column_index = 5
            end_dc_file = str(pandas_entry_for_first_row[column_index])
            _item = QTableWidgetItem(end_dc_file)
            o_table.insert_item(row=_row, column=column_index, item=_item)

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
            list_procedure = list_fit_procedure
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
            result_directory = str(pandas_entry_for_first_row[column_index])
            _item = QTableWidgetItem(result_directory)
            o_table.insert_item(row=_row, column=column_index, item=_item)

            # file_id
            column_index = 24
            file_id_value = str(pandas_entry_for_this_row[column_index])
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

    def cancel_button_pushed(self):
        self.close()

    def save_as_button_pushed(self):
        working_dir = self.grand_parent.working_dir
        folder_selected = self.grand_parent.folder_selected
        base_folder_name = os.path.basename(folder_selected)
        default_file_name = os.path.join(working_dir, base_folder_name + "_angel_excel.xls")
        file_and_extension_name = QFileDialog.getSaveFileName(self,
                                                              "Select or define file name",
                                                              default_file_name,
                                                              "Excel (*.xls)")

        file_name = file_and_extension_name[0]
        if file_name:
            table_dict = self.collect_table_dict()

        df = pd.DataFrame(table_dict)
        writer = pd.ExcelWriter(file_name,
                                engine='xlsxwriter')
        df.to_excel(writer, sheet_name="Tabelle1",
                            index=False)
        writer.save()

    def collect_table_dict(self):
        o_table = TableHandler(table_ui=self.ui.tableWidget)
        nbr_rows = o_table.row_count()

        first_data_file = []
        last_data_file = []
        first_ob_file = []
        last_ob_file = []
        first_dc_file = []
        last_dc_file = []
        period = []
        images_per_step = []
        rotation = []
        fit_procedure = []
        roi = []
        gamma_filter_data_ob = []
        data_threshold_3x3 = []
        data_threshold_5x5 = []
        data_threshold_7x7 = []
        data_sigma_log = []
        gamma_filter_dc = []
        dc_threshold_3x3 = []
        dc_threshold_5x5 = []
        dc_threshold_7x7 = []
        dc_sigma_log = []
        dc_outlier_removal = []
        dc_outlier_value = []
        result_directory = []
        file_id = []
        sample_information = []
        used_environment = []
        osc_pixel = []

        for _row in np.arange(nbr_rows):

            o_table.set_row(row=_row)
            first_data_file.append(o_table.get_first_data_file())
            last_data_file.append(o_table.get_last_data_file())
            first_ob_file.append(o_table.get_first_ob_file())
            last_ob_file.append(o_table.get_last_ob_file())
            first_dc_file.append(o_table.get_first_dc_file())
            last_dc_file.append(o_table.get_last_dc_file())
            period.append(o_table.get_period())
            images_per_step.append(o_table.get_images_per_step())
            rotation.append(o_table.get_rotation())
            fit_procedure.append(o_table.get_fit_procedure())
            roi.append(o_table.get_roi())
            gamma_filter_data_ob.append(o_table.get_gamma_filter_data_ob())
            data_threshold_3x3.append(o_table.get_data_threshold_3x3())
            data_threshold_5x5.append(o_table.get_data_threshold_5x5())
            data_threshold_7x7.append(o_table.get_data_threshold_7x7())
            data_sigma_log.append(o_table.get_data_sigma_log())
            gamma_filter_dc.append(o_table.get_gamma_filter_dc())
            dc_threshold_3x3.append(o_table.get_dc_threshold_3x3())
            dc_threshold_5x5.append(o_table.get_dc_threshold_5x5())
            dc_threshold_7x7.append(o_table.get_dc_threshold_7x7())
            dc_sigma_log.append(o_table.get_dc_log())
            dc_outlier_removal.append(o_table.get_dc_outlier_removal())
            dc_outlier_value.append(o_table.get_dc_outlier_value())
            result_directory.append(o_table.get_result_directory())
            file_id.append(o_table.get_file_id())
            sample_information.append("")
            used_environment.append("")
            osc_pixel.append("")

        table_dict = OrderedDict({'first_data_file'     : first_data_file,
                                  'last_data_file'      : last_data_file,
                                  'first_ob_file'       : first_ob_file,
                                  'last_ob_file'        : last_ob_file,
                                  'first_dc_file'       : first_dc_file,
                                  'last_dc_file'        : last_dc_file,
                                  'period'              : period,
                                  'images_per_step'     : images_per_step,
                                  'rotation'            : rotation,
                                  'fit_procedure'       : fit_procedure,
                                  'roi'                 : roi,
                                  'gamma_filter_data/ob': gamma_filter_data_ob,
                                  'data_threshold_3x3'  : data_threshold_3x3,
                                  'data_threshold_5x5'  : data_threshold_5x5,
                                  'data_threshold_7x7'  : data_threshold_7x7,
                                  'data_sigma_log'      : data_sigma_log,
                                  'gamma_filter_dc'     : gamma_filter_dc,
                                  'dc_threshold_3x3'    : dc_threshold_3x3,
                                  'dc_threshold_5x5'    : dc_threshold_5x5,
                                  'dc_threshold_7x7'    : dc_threshold_7x7,
                                  'dc_sigma_log'        : dc_sigma_log,
                                  'dc_outlier_removal'  : dc_outlier_removal,
                                  'dc_outlier_value'    : dc_outlier_value,
                                  'result_directory'    : result_directory,
                                  'file_id'             : file_id,
                                  'sample_information'  : sample_information,
                                  'used_environment'    : used_environment,
                                  'osc_pixel'           : osc_pixel,
                                  })

        return table_dict

    def right_click_table_widget(self, position):
        menu = QMenu(self)

        print(position)

        remove = menu.addAction("Remove selected row")
        add = menu.addAction("Add row at bottom")

        menu.addSeparator()

        browse = menu.addAction("Browse ...")

        action = menu.exec_(QtGui.QCursor.pos())

        if action == remove:
            self.remove_row()
        elif action == add:
            self.add_row_at_bottom()

    def remove_selected_row(self):
        pass

    def add_row_at_bottom(self):
        pass

    def browse_for_file(self):
        pass
