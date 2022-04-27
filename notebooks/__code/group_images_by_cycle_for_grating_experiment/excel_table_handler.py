from qtpy.QtWidgets import QTableWidgetItem, QSpinBox, QComboBox
from qtpy import QtCore

from __code._utilities.table_handler import TableHandler
from __code.group_images_by_cycle_for_grating_experiment import list_fit_procedure
from __code.group_images_by_cycle_for_grating_experiment import IndexOfColumns


class ExcelTableHandler(TableHandler):

    def define_row_for_setter(self, row=0):
        self.row_to_set = row

    def define_row_for_getter(self, row=0):
        self.get_from_row = row

    def set_value(self, column=0, value=""):
        _item = QTableWidgetItem(str(value))
        self.insert_item(row=self.row_to_set, column=column, item=_item)

    def get_first_data_file(self):
        column = IndexOfColumns.first_data_file
        return self.get_item_str_from_cell(row=self.get_from_row, column=column)

    def set_first_data_file(self, value):
        column = IndexOfColumns.first_data_file
        self.set_value(column=column, value=value)

    def get_last_data_file(self):
        column = IndexOfColumns.last_data_file
        return self.get_item_str_from_cell(row=self.get_from_row, column=column)

    def set_last_data_file(self, value):
        column = IndexOfColumns.last_data_file
        self.set_value(column=column, value=value)

    def get_first_ob_file(self):
        column = IndexOfColumns.first_ob_file
        return self.get_item_str_from_cell(row=self.get_from_row, column=column)

    def set_first_ob_file(self, value):
        column = IndexOfColumns.first_ob_file
        self.set_value(column=column, value=value)

    def get_last_ob_file(self):
        column = IndexOfColumns.last_ob_file
        return self.get_item_str_from_cell(row=self.get_from_row, column=column)

    def set_last_ob_file(self, value):
        column = IndexOfColumns.last_ob_file
        self.set_value(column=column, value=value)

    def get_first_dc_file(self):
        column = IndexOfColumns.first_dc_file
        return self.get_item_str_from_cell(row=self.get_from_row, column=column)

    def set_first_dc_file(self, value):
        column = IndexOfColumns.first_dc_file
        self.set_value(column=column, value=value)

    def get_last_dc_file(self):
        column = IndexOfColumns.last_dc_file
        return self.get_item_str_from_cell(row=self.get_from_row, column=column)

    def set_last_dc_file(self, value):
        column = IndexOfColumns.last_dc_file
        self.set_value(column=column, value=value)

    def get_period(self):
        column = IndexOfColumns.period
        widget = self.get_widget(row=self.get_from_row, column=column)
        return widget.value()

    def set_period(self, value, method=None, new=True):
        column = IndexOfColumns.period
        if new:
            period_widget = QSpinBox()
            period_widget.setMinimum(1)
            period_widget.setMaximum(10)
            period_widget.setValue(int(value))
            self.insert_widget(row=self.row_to_set, column=column, widget=period_widget)
            period_widget.valueChanged.connect(lambda value, row=self.row_to_set, column=column: method(value, row,
                                                                                                column))
        else:
            period_widget = self.get_widget(row=self.row_to_set,
                                            column=column)
            period_widget.blockSignals(True)
            period_widget.setValue(int(value))
            period_widget.blockSignals(False)

    def get_images_per_step(self):
        column = IndexOfColumns.images_per_step
        widget = self.get_widget(row=self.get_from_row, column=column)
        return widget.value()

    def set_images_per_step(self, value, method=None, new=True):
        column = IndexOfColumns.images_per_step
        if new:
            images_per_step = QSpinBox()
            images_per_step_value = value
            images_per_step.setMinimum(1)
            images_per_step.setMaximum(10)
            images_per_step.setValue(images_per_step_value)
            self.insert_widget(row=self.row_to_set, column=column, widget=images_per_step)
            images_per_step.valueChanged.connect(lambda value, row=self.row_to_set, column=column: method(value, row,
                                                                                                          column))
        else:
            images_per_step = self.get_widget(row=self.row_to_set,
                                              column=column)
            images_per_step.blockSignals(True)
            images_per_step.setValue(int(value))
            images_per_step.blockSignals(False)

    def get_rotation(self):
        column = IndexOfColumns.rotation
        return float(self.get_item_str_from_cell(row=self.get_from_row, column=column))

    def set_rotation(self, value):
        column = IndexOfColumns.rotation
        rotation_value = str(value)
        item = QTableWidgetItem(rotation_value)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        self.insert_item(row=self.row_to_set, column=column, item=item)

    def get_fit_procedure(self):
        column = IndexOfColumns.fit_procedure
        widget = self.get_widget(row=self.get_from_row, column=column)
        return widget.currentText()

    def get_fit_procedure_index(self):
        column = IndexOfColumns.fit_procedure
        widget = self.get_widget(row=self.get_from_row, column=column)
        return widget.currentIndex()

    def set_fit_procedure(self, value, method=None, new=True):
        column = IndexOfColumns.fit_procedure
        if new:
            fit_procedure = QComboBox()
            fit_procedure_value = value
            list_procedure = list_fit_procedure
            fit_procedure.addItems(list_procedure)
            index = list_procedure.index(fit_procedure_value)
            fit_procedure.setCurrentIndex(index)
            self.insert_widget(row=self.row_to_set, column=column, widget=fit_procedure)
            fit_procedure.currentIndexChanged.connect(lambda value, row=self.row_to_set, column=column: method(value,
                                                                                                               row, column))
        else:
            fit_procedure = self.get_widget(row=self.row_to_set,
                                            column=column)
            fit_procedure.blockSignals(True)
            fit_procedure.setCurrentIndex(value)
            fit_procedure.blockSignals(False)

    def get_roi(self):
        column = IndexOfColumns.roi
        return self.get_item_str_from_cell(row=self.get_from_row, column=column)

    def set_roi(self, value):
        column = IndexOfColumns.roi
        roi_value = value
        roi_item = QTableWidgetItem(roi_value)
        self.insert_item(row=self.row_to_set, column=column, item=roi_item)

    def get_gamma_filter_data_ob(self):
        column = IndexOfColumns.gamma_filter_data_ob
        widget = self.get_widget(row=self.get_from_row, column=column)
        return widget.currentText()

    def get_gamma_filter_data_ob_index(self):
        column = IndexOfColumns.gamma_filter_data_ob
        widget = self.get_widget(row=self.get_from_row, column=column)
        return widget.currentIndex()

    def set_gamma_filter_data_ob(self, value, method=None, new=True):
        column = IndexOfColumns.gamma_filter_data_ob
        if new:
            gamma_filter_value = str(value)
            values = ['yes', 'no']
            gamma_filter_ui = QComboBox()
            gamma_filter_ui.addItems(values)
            gamma_filter_ui.setCurrentText(gamma_filter_value)
            self.insert_widget(row=self.row_to_set, column=column, widget=gamma_filter_ui)
            gamma_filter_ui.currentIndexChanged.connect(lambda value, row=self.row_to_set, column=column: method(value,
                                                                                                                 row,
                                                                                                                 column))
        else:
            gamma_filter_ui = self.get_widget(row=self.row_to_set,
                                              column=column)
            gamma_filter_ui.blockSignals(True)
            gamma_filter_ui.setCurrentIndex(value)
            gamma_filter_ui.blockSignals(False)

    def get_data_threshold_3x3(self):
        column = IndexOfColumns.data_threshold_3x3
        return int(self.get_item_str_from_cell(row=self.get_from_row, column=column))

    def set_data_threshold_3x3(self, value):
        column = IndexOfColumns.data_threshold_3x3
        data_threshold_3x3_value = str(value)
        item_data_3x3 = QTableWidgetItem(data_threshold_3x3_value)
        self.insert_item(row=self.row_to_set, column=column, item=item_data_3x3)

    def get_data_threshold_5x5(self):
        column = IndexOfColumns.data_threshold_5x5
        return int(self.get_item_str_from_cell(row=self.get_from_row, column=column))

    def set_data_threshold_5x5(self, value):
        column = IndexOfColumns.data_threshold_5x5
        data_threshold_5x5_value = str(value)
        item_data_5x5 = QTableWidgetItem(data_threshold_5x5_value)
        self.insert_item(row=self.row_to_set, column=column, item=item_data_5x5)

    def get_data_threshold_7x7(self):
        column = IndexOfColumns.data_threshold_7x7
        return int(self.get_item_str_from_cell(row=self.get_from_row, column=column))

    def set_data_threshold_7x7(self, value):
        column = IndexOfColumns.data_threshold_7x7
        data_threshold_7x7_value = str(value)
        item_data_7x7 = QTableWidgetItem(data_threshold_7x7_value)
        self.insert_item(row=self.row_to_set, column=column, item=item_data_7x7)

    def get_data_sigma_log(self):
        column = IndexOfColumns.data_sigma_log
        return float(self.get_item_str_from_cell(row=self.get_from_row, column=column))

    def set_data_sigma_log(self, value):
        column = IndexOfColumns.data_sigma_log
        data_sigma_log_value = str(value)
        item_data_sigma = QTableWidgetItem(data_sigma_log_value)
        self.insert_item(row=self.row_to_set, column=column, item=item_data_sigma)

    def get_gamma_filter_dc(self):
        column = IndexOfColumns.gamma_filter_dc
        widget = self.get_widget(row=self.get_from_row, column=column)
        return widget.currentText()

    def get_gamma_filter_dc_index(self):
        column = IndexOfColumns.gamma_filter_dc
        widget = self.get_widget(row=self.get_from_row, column=column)
        return widget.currentIndex()

    def set_gamma_filter_dc(self, value, method=None, new=True):
        column = IndexOfColumns.gamma_filter_dc
        if new:
            gamma_filter_value = value
            values = ['yes', 'no']
            gamma_filter_dc_ui = QComboBox()
            gamma_filter_dc_ui.addItems(values)
            gamma_filter_dc_ui.setCurrentText(gamma_filter_value)
            self.insert_widget(row=self.row_to_set, column=column, widget=gamma_filter_dc_ui)
            gamma_filter_dc_ui.currentIndexChanged.connect(lambda value, row=self.row_to_set, column=column: method(
                    value, row, column))
        else:
            gamma_filter_dc_ui = self.get_widget(row=self.row_to_set,
                                                 column=column)
            gamma_filter_dc_ui.blockSignals(True)
            gamma_filter_dc_ui.setCurrentIndex(value)
            gamma_filter_dc_ui.blockSignals(False)

    def get_dc_threshold_3x3(self):
        column = IndexOfColumns.dc_threshold_3x3
        return int(self.get_item_str_from_cell(row=self.get_from_row, column=column))

    def set_dc_threshold_3x3(self, value):
        column = IndexOfColumns.dc_threshold_3x3
        dc_threshold_3x3_value = str(value)
        item_dc_3x3 = QTableWidgetItem(dc_threshold_3x3_value)
        self.insert_item(row=self.row_to_set, column=column, item=item_dc_3x3)

    def get_dc_threshold_5x5(self):
        column = IndexOfColumns.dc_threhsold_5x5
        return int(self.get_item_str_from_cell(row=self.get_from_row, column=column))

    def set_dc_threshold_5x5(self, value):
        column = IndexOfColumns.dc_threhsold_5x5
        dc_threshold_5x5_value = str(value)
        item_dc_5x5 = QTableWidgetItem(dc_threshold_5x5_value)
        self.insert_item(row=self.row_to_set, column=column, item=item_dc_5x5)

    def get_dc_threshold_7x7(self):
        column = IndexOfColumns.dc_threshold_7x7
        return int(self.get_item_str_from_cell(row=self.get_from_row, column=column))

    def set_dc_threshold_7x7(self, value):
        column = IndexOfColumns.dc_threshold_7x7
        dc_threshold_7x7_value = str(value)
        item_dc_7x7 = QTableWidgetItem(dc_threshold_7x7_value)
        self.insert_item(row=self.row_to_set, column=column, item=item_dc_7x7)

    def get_dc_log(self):
        column = IndexOfColumns.dc_log
        return float(self.get_item_str_from_cell(row=self.get_from_row, column=column))

    def set_dc_log(self, value):
        column = IndexOfColumns.dc_log
        dc_sigma_log_value = str(value)
        item_dc_sigma = QTableWidgetItem(dc_sigma_log_value)
        self.insert_item(row=self.row_to_set, column=column, item=item_dc_sigma)

    def get_dc_outlier_removal(self):
        column = IndexOfColumns.dc_outlier_removal
        widget = self.get_widget(row=self.get_from_row, column=column)
        return widget.currentText()

    def get_dc_outlier_removal_index(self):
        column = IndexOfColumns.dc_outlier_removal
        widget = self.get_widget(row=self.get_from_row, column=column)
        return widget.currentIndex()

    def set_dc_outlier_removal(self, value, method=None, new=True):
        column = IndexOfColumns.dc_outlier_removal
        if new:
            dc_outlier_value = value
            values = ['yes', 'no']
            dc_outlier_ui = QComboBox()
            dc_outlier_ui.addItems(values)
            dc_outlier_ui.setCurrentText(dc_outlier_value)
            self.insert_widget(row=self.row_to_set, column=column, widget=dc_outlier_ui)
            dc_outlier_ui.currentIndexChanged.connect(lambda value, row=self.row_to_set, column=column: method(value,
                                                                                                               row, column))
        else:
            dc_outlier_ui = self.get_widget(row=self.row_to_set,
                                            column=column)
            dc_outlier_ui.blockSignals(True)
            dc_outlier_ui.setCurrentIndex(value)
            dc_outlier_ui.blockSignals(False)

    def get_dc_outlier_value(self):
        column = IndexOfColumns.dc_outlier_value
        return float(self.get_item_str_from_cell(row=self.get_from_row, column=column))

    def set_dc_outlier_value(self, value):
        column = IndexOfColumns.dc_outlier_value
        dc_outlier_value = str(value)
        dc_outlier = QTableWidgetItem(dc_outlier_value)
        self.insert_item(row=self.row_to_set, column=column, item=dc_outlier)

    def get_result_directory(self):
        column = IndexOfColumns.result_directory
        return self.get_item_str_from_cell(row=self.get_from_row, column=column)

    def set_result_directory(self, value):
        column = IndexOfColumns.result_directory
        result_directory = str(value)
        _item = QTableWidgetItem(result_directory)
        self.insert_item(row=self.row_to_set, column=column, item=_item)

    def get_file_id(self):
        column = IndexOfColumns.file_id
        return self.get_item_str_from_cell(row=self.get_from_row, column=column)

    def set_file_id(self, value):
        column = IndexOfColumns.file_id
        file_id_value = str(value)
        file_id = QTableWidgetItem(file_id_value)
        self.insert_item(row=self.row_to_set, column=column, item=file_id)
