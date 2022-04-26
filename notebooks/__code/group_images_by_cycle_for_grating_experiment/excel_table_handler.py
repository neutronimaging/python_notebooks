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
        self.set_value(column=0, value=value)

    def get_last_data_file(self):
        return self.get_item_str_from_cell(row=self.get_from_row, column=1)

    def set_last_data_file(self, value):
        self.set_value(column=1, value=value)

    def get_first_ob_file(self):
        return self.get_item_str_from_cell(row=self.get_from_row, column=2)

    def set_first_ob_file(self, value):
        self.set_value(column=2, value=value)

    def get_last_ob_file(self):
        return self.get_item_str_from_cell(row=self.get_from_row, column=3)

    def set_last_ob_file(self, value):
        self.set_value(column=3, value=value)

    def get_first_dc_file(self):
        return self.get_item_str_from_cell(row=self.get_from_row, column=4)

    def set_first_dc_file(self, value):
        self.set_value(column=4, value=value)

    def get_last_dc_file(self):
        return self.get_item_str_from_cell(row=self.get_from_row, column=5)

    def set_last_dc_file(self, value):
        self.set_value(column=5, value=value)

    def get_period(self):
        widget = self.get_widget(row=self.get_from_row, column=6)
        return widget.value()

    def set_period(self, value, method=None, column=0):
        period_widget = QSpinBox()
        period_widget.setMinimum(1)
        period_widget.setMaximum(10)
        period_widget.setValue(int(value))
        self.insert_widget(row=self.row_to_set, column=6, widget=period_widget)
        period_widget.valueChanged.connect(lambda value, row=self.row_to_set, column=column: method(value, row, column))

    def get_images_per_step(self):
        widget = self.get_widget(row=self.get_from_row, column=7)
        return widget.value()

    def set_images_per_step(self, value):
        images_per_step = QSpinBox()
        images_per_step_value = value
        images_per_step.setMinimum(1)
        images_per_step.setMaximum(10)
        images_per_step.setValue(images_per_step_value)
        self.insert_widget(row=self.row_to_set, column=7, widget=images_per_step)

    def get_rotation(self):
        return float(self.get_item_str_from_cell(row=self.get_from_row, column=8))

    def set_rotation(self, value):
        rotation_value = str(value)
        item = QTableWidgetItem(rotation_value)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        self.insert_item(row=self.row_to_set, column=8, item=item)

    def get_fit_procedure(self):
        widget = self.get_widget(row=self.get_from_row, column=9)
        return widget.currentText()

    def set_fit_procedure(self, value):
        fit_procedure = QComboBox()
        fit_procedure_value = value
        list_procedure = list_fit_procedure
        fit_procedure.addItems(list_procedure)
        index = list_procedure.index(fit_procedure_value)
        fit_procedure.setCurrentIndex(index)
        self.insert_widget(row=self.row_to_set, column=9, widget=fit_procedure)

    def get_roi(self):
        return self.get_item_str_from_cell(row=self.get_from_row, column=10)

    def set_roi(self, value):
        roi_value = value
        roi_item = QTableWidgetItem(roi_value)
        self.insert_item(row=self.row_to_set, column=10, item=roi_item)

    def get_gamma_filter_data_ob(self):
        widget = self.get_widget(row=self.get_from_row, column=11)
        return widget.currentText()

    def set_gamma_filter_data_ob(self, value):
        gamma_filter_value = str(value)
        values = ['yes', 'no']
        gamma_filter_ui = QComboBox()
        gamma_filter_ui.addItems(values)
        gamma_filter_ui.setCurrentText(gamma_filter_value)
        self.insert_widget(row=self.row_to_set, column=11, widget=gamma_filter_ui)

    def get_data_threshold_3x3(self):
        return int(self.get_item_str_from_cell(row=self.get_from_row, column=12))

    def set_data_threshold_3x3(self, value):
        data_threshold_3x3_value = str(value)
        item_data_3x3 = QTableWidgetItem(data_threshold_3x3_value)
        self.insert_item(row=self.row_to_set, column=12, item=item_data_3x3)

    def get_data_threshold_5x5(self):
        return int(self.get_item_str_from_cell(row=self.get_from_row, column=13))

    def set_data_threshold_5x5(self, value):
        data_threshold_5x5_value = str(value)
        item_data_5x5 = QTableWidgetItem(data_threshold_5x5_value)
        self.insert_item(row=self.row_to_set, column=13, item=item_data_5x5)

    def get_data_threshold_7x7(self):
        return int(self.get_item_str_from_cell(row=self.get_from_row, column=14))

    def set_data_threshold_7x7(self, value):
        data_threshold_7x7_value = str(value)
        item_data_7x7 = QTableWidgetItem(data_threshold_7x7_value)
        self.insert_item(row=self.row_to_set, column=14, item=item_data_7x7)

    def get_data_sigma_log(self):
        return float(self.get_item_str_from_cell(row=self.get_from_row, column=15))

    def set_data_sigma_log(self, value):
        data_sigma_log_value = str(value)
        item_data_sigma = QTableWidgetItem(data_sigma_log_value)
        self.insert_item(row=self.row_to_set, column=15, item=item_data_sigma)

    def get_gamma_filter_dc(self):
        widget = self.get_widget(row=self.get_from_row, column=16)
        return widget.currentText()

    def set_gamma_filter_dc(self, value):
        gamma_filter_value = value
        values = ['yes', 'no']
        gamma_filter_dc_ui = QComboBox()
        gamma_filter_dc_ui.addItems(values)
        gamma_filter_dc_ui.setCurrentText(gamma_filter_value)
        self.insert_widget(row=self.row_to_set, column=16, widget=gamma_filter_dc_ui)

    def get_dc_threshold_3x3(self):
        return int(self.get_item_str_from_cell(row=self.get_from_row, column=17))

    def set_dc_threshold_3x3(self, value):
        dc_threshold_3x3_value = str(value)
        item_dc_3x3 = QTableWidgetItem(dc_threshold_3x3_value)
        self.insert_item(row=self.row_to_set, column=17, item=item_dc_3x3)

    def get_dc_threshold_5x5(self):
        return int(self.get_item_str_from_cell(row=self.get_from_row, column=18))

    def set_dc_threshold_5x5(self, value):
        dc_threshold_5x5_value = str(value)
        item_dc_5x5 = QTableWidgetItem(dc_threshold_5x5_value)
        self.insert_item(row=self.row_to_set, column=18, item=item_dc_5x5)

    def get_dc_threshold_7x7(self):
        return int(self.get_item_str_from_cell(row=self.get_from_row, column=19))

    def set_dc_threshold_7x7(self, value):
        dc_threshold_7x7_value = str(value)
        item_dc_7x7 = QTableWidgetItem(dc_threshold_7x7_value)
        self.insert_item(row=self.row_to_set, column=19, item=item_dc_7x7)

    def get_dc_log(self):
        return float(self.get_item_str_from_cell(row=self.get_from_row, column=20))

    def set_dc_log(self, value):
        dc_sigma_log_value = str(value)
        item_dc_sigma = QTableWidgetItem(dc_sigma_log_value)
        self.insert_item(row=self.row_to_set, column=20, item=item_dc_sigma)

    def get_dc_outlier_removal(self):
        widget = self.get_widget(row=self.get_from_row, column=21)
        return widget.currentText()

    def set_dc_outlier_removal(self, value):
        dc_outlier_value = value
        values = ['yes', 'no']
        dc_outlier_ui = QComboBox()
        dc_outlier_ui.addItems(values)
        dc_outlier_ui.setCurrentText(dc_outlier_value)
        self.insert_widget(row=self.row_to_set, column=21, widget=dc_outlier_ui)

    def get_dc_outlier_value(self):
        return float(self.get_item_str_from_cell(row=self.get_from_row, column=22))

    def set_dc_outlier_value(self, value):
        dc_outlier_value = str(value)
        dc_outlier = QTableWidgetItem(dc_outlier_value)
        self.insert_item(row=self.row_to_set, column=22, item=dc_outlier)

    def get_result_directory(self):
        return self.get_item_str_from_cell(row=self.get_from_row, column=23)

    def set_result_directory(self, value):
        result_directory = str(value)
        _item = QTableWidgetItem(result_directory)
        self.insert_item(row=self.row_to_set, column=23, item=_item)

    def get_file_id(self):
        return self.get_item_str_from_cell(row=self.get_from_row, column=24)

    def set_file_id(self, value):
        file_id_value = str(value)
        file_id = QTableWidgetItem(file_id_value)
        self.insert_item(row=self.row_to_set, column=24, item=file_id)
