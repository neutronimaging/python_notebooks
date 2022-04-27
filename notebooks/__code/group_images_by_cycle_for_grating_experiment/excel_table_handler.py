from qtpy.QtWidgets import QTableWidgetItem, QSpinBox, QComboBox
from qtpy import QtCore
import copy

from __code._utilities.table_handler import TableHandler
from __code.group_images_by_cycle_for_grating_experiment import list_fit_procedure


class ExcelTableHandler(TableHandler):

    def define_row_for_setter(self, row=0):
        self.row_to_set = row

    def define_row_for_getter(self, row=0):
        self.get_from_row = row

    def set_value(self, column=0, value=""):
        _item = QTableWidgetItem(str(value))
        self.insert_item(row=self.row_to_set, column=column, item=_item)

    def get_first_data_file(self):
        return self.get_item_str_from_cell(row=self.get_from_row, column=0)

    def set_first_data_file(self, value):
        column = 0
        self.set_value(column=column, value=value)

    def get_last_data_file(self):
        return self.get_item_str_from_cell(row=self.get_from_row, column=1)

    def set_last_data_file(self, value):
        column = 1
        self.set_value(column=column, value=value)

    def get_first_ob_file(self):
        return self.get_item_str_from_cell(row=self.get_from_row, column=2)

    def set_first_ob_file(self, value):
        column = 2
        self.set_value(column=column, value=value)

    def get_last_ob_file(self):
        return self.get_item_str_from_cell(row=self.get_from_row, column=3)

    def set_last_ob_file(self, value):
        column = 3
        self.set_value(column=column, value=value)

    def get_first_dc_file(self):
        return self.get_item_str_from_cell(row=self.get_from_row, column=4)

    def set_first_dc_file(self, value):
        column = 4
        self.set_value(column=column, value=value)

    def get_last_dc_file(self):
        return self.get_item_str_from_cell(row=self.get_from_row, column=5)

    def set_last_dc_file(self, value):
        column = 5
        self.set_value(column=column, value=value)

    def get_period(self):
        widget = self.get_widget(row=self.get_from_row, column=6)
        return widget.value()

    def set_period(self, value, method=None, new=True):
        column = 6
        if new:
            period_widget = QSpinBox()
            period_widget.setMinimum(1)
            period_widget.setMaximum(10)
            period_widget.setValue(int(value))
            self.insert_widget(row=self.row_to_set, column=column, widget=period_widget)
            period_widget.valueChanged.connect(lambda value, row=self.row_to_set, column=column: method(value,
                                                                                                        row,
                                                                                                        column))
        else:
            period_widget = self.get_widget(row=self.row_to_set,
                                            column=column)

    def get_images_per_step(self):
        column = 7
        widget = self.get_widget(row=self.get_from_row, column=column)
        return widget.value()

    def set_images_per_step(self, value, method=None):
        column = 7
        images_per_step = QSpinBox()
        images_per_step_value = value
        images_per_step.setMinimum(1)
        images_per_step.setMaximum(10)
        images_per_step.setValue(images_per_step_value)
        self.insert_widget(row=self.row_to_set, column=column, widget=images_per_step)
        images_per_step.valueChanged.connect(lambda value, row=self.row_to_set, column=column: method(value, row,
                                                                                                      column))

    def get_rotation(self):
        column = 8
        return float(self.get_item_str_from_cell(row=self.get_from_row, column=column))

    def set_rotation(self, value):
        column = 8
        rotation_value = str(value)
        item = QTableWidgetItem(rotation_value)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        self.insert_item(row=self.row_to_set, column=column, item=item)

    def get_fit_procedure(self):
        column = 9
        widget = self.get_widget(row=self.get_from_row, column=column)
        return widget.currentText()

    def set_fit_procedure(self, value, method=None):
        column = 9
        fit_procedure = QComboBox()
        fit_procedure_value = value
        list_procedure = list_fit_procedure
        fit_procedure.addItems(list_procedure)
        index = list_procedure.index(fit_procedure_value)
        fit_procedure.setCurrentIndex(index)
        self.insert_widget(row=self.row_to_set, column=column, widget=fit_procedure)
        fit_procedure.currentIndexChanged.connect(lambda value, row=self.row_to_set, column=column: method(value,
                                                                                                           row, column))

    def get_roi(self):
        column = 10
        return self.get_item_str_from_cell(row=self.get_from_row, column=column)

    def set_roi(self, value):
        column = 10
        roi_value = value
        roi_item = QTableWidgetItem(roi_value)
        self.insert_item(row=self.row_to_set, column=column, item=roi_item)

    def get_gamma_filter_data_ob(self):
        column = 11
        widget = self.get_widget(row=self.get_from_row, column=column)
        return widget.currentText()

    def set_gamma_filter_data_ob(self, value, method=None):
        column = 11
        gamma_filter_value = str(value)
        values = ['yes', 'no']
        gamma_filter_ui = QComboBox()
        gamma_filter_ui.addItems(values)
        gamma_filter_ui.setCurrentText(gamma_filter_value)
        self.insert_widget(row=self.row_to_set, column=column, widget=gamma_filter_ui)
        gamma_filter_ui.currentIndexChanged.connect(lambda value, row=self.row_to_set, column=column: method(value,
                                                                                                             row,
                                                                                                             column))

    def get_data_threshold_3x3(self):
        column = 12
        return int(self.get_item_str_from_cell(row=self.get_from_row, column=column))

    def set_data_threshold_3x3(self, value):
        column = 12
        data_threshold_3x3_value = str(value)
        item_data_3x3 = QTableWidgetItem(data_threshold_3x3_value)
        self.insert_item(row=self.row_to_set, column=column, item=item_data_3x3)

    def get_data_threshold_5x5(self):
        column = 13
        return int(self.get_item_str_from_cell(row=self.get_from_row, column=column))

    def set_data_threshold_5x5(self, value):
        column = 13
        data_threshold_5x5_value = str(value)
        item_data_5x5 = QTableWidgetItem(data_threshold_5x5_value)
        self.insert_item(row=self.row_to_set, column=column, item=item_data_5x5)

    def get_data_threshold_7x7(self):
        column = 14
        return int(self.get_item_str_from_cell(row=self.get_from_row, column=column))

    def set_data_threshold_7x7(self, value):
        column = 14
        data_threshold_7x7_value = str(value)
        item_data_7x7 = QTableWidgetItem(data_threshold_7x7_value)
        self.insert_item(row=self.row_to_set, column=column, item=item_data_7x7)

    def get_data_sigma_log(self):
        column = 15
        return float(self.get_item_str_from_cell(row=self.get_from_row, column=column))

    def set_data_sigma_log(self, value):
        column = 15
        data_sigma_log_value = str(value)
        item_data_sigma = QTableWidgetItem(data_sigma_log_value)
        self.insert_item(row=self.row_to_set, column=column, item=item_data_sigma)

    def get_gamma_filter_dc(self):
        column = 16
        widget = self.get_widget(row=self.get_from_row, column=column)
        return widget.currentText()

    def set_gamma_filter_dc(self, value, method=None):
        column = 16
        gamma_filter_value = value
        values = ['yes', 'no']
        gamma_filter_dc_ui = QComboBox()
        gamma_filter_dc_ui.addItems(values)
        gamma_filter_dc_ui.setCurrentText(gamma_filter_value)
        self.insert_widget(row=self.row_to_set, column=column, widget=gamma_filter_dc_ui)
        gamma_filter_dc_ui.currentIndexChanged.connect(lambda value, row=self.row_to_set, column=column: method(
                value, row, column))

    def get_dc_threshold_3x3(self):
        column = 17
        return int(self.get_item_str_from_cell(row=self.get_from_row, column=column))

    def set_dc_threshold_3x3(self, value):
        column = 17
        dc_threshold_3x3_value = str(value)
        item_dc_3x3 = QTableWidgetItem(dc_threshold_3x3_value)
        self.insert_item(row=self.row_to_set, column=column, item=item_dc_3x3)

    def get_dc_threshold_5x5(self):
        column = 18
        return int(self.get_item_str_from_cell(row=self.get_from_row, column=column))

    def set_dc_threshold_5x5(self, value):
        column = 18
        dc_threshold_5x5_value = str(value)
        item_dc_5x5 = QTableWidgetItem(dc_threshold_5x5_value)
        self.insert_item(row=self.row_to_set, column=column, item=item_dc_5x5)

    def get_dc_threshold_7x7(self):
        column = 19
        return int(self.get_item_str_from_cell(row=self.get_from_row, column=column))

    def set_dc_threshold_7x7(self, value):
        column = 19
        dc_threshold_7x7_value = str(value)
        item_dc_7x7 = QTableWidgetItem(dc_threshold_7x7_value)
        self.insert_item(row=self.row_to_set, column=column, item=item_dc_7x7)

    def get_dc_log(self):
        column = 20
        return float(self.get_item_str_from_cell(row=self.get_from_row, column=column))

    def set_dc_log(self, value):
        column = 20
        dc_sigma_log_value = str(value)
        item_dc_sigma = QTableWidgetItem(dc_sigma_log_value)
        self.insert_item(row=self.row_to_set, column=column, item=item_dc_sigma)

    def get_dc_outlier_removal(self):
        column = 21
        widget = self.get_widget(row=self.get_from_row, column=column)
        return widget.currentText()

    def set_dc_outlier_removal(self, value, method=None):
        column = 21
        dc_outlier_value = value
        values = ['yes', 'no']
        dc_outlier_ui = QComboBox()
        dc_outlier_ui.addItems(values)
        dc_outlier_ui.setCurrentText(dc_outlier_value)
        self.insert_widget(row=self.row_to_set, column=column, widget=dc_outlier_ui)
        dc_outlier_ui.currentIndexChanged.connect(lambda value, row=self.row_to_set, column=column: method(value,
                                                                                                           row, column))

    def get_dc_outlier_value(self):
        column = 22
        return float(self.get_item_str_from_cell(row=self.get_from_row, column=column))

    def set_dc_outlier_value(self, value):
        column = 22
        dc_outlier_value = str(value)
        dc_outlier = QTableWidgetItem(dc_outlier_value)
        self.insert_item(row=self.row_to_set, column=column, item=dc_outlier)

    def get_result_directory(self):
        column = 23
        return self.get_item_str_from_cell(row=self.get_from_row, column=column)

    def set_result_directory(self, value):
        column = 23
        result_directory = str(value)
        _item = QTableWidgetItem(result_directory)
        self.insert_item(row=self.row_to_set, column=column, item=_item)

    def get_file_id(self):
        column = 24
        return self.get_item_str_from_cell(row=self.get_from_row, column=column)

    def set_file_id(self, value):
        column = 24
        file_id_value = str(value)
        file_id = QTableWidgetItem(file_id_value)
        self.insert_item(row=self.row_to_set, column=column, item=file_id)
