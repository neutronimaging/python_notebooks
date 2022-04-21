from __code._utilities.table_handler import TableHandler


class ExcelTableHandler(TableHandler):

    def set_row(self, row=0):
        self.row = row

    def get_first_data_file(self):
        return self.get_item_str_from_cell(row=self.row, column=0)

    def get_last_data_file(self):
        return self.get_item_str_from_cell(row=self.row, column=1)

    def get_first_ob_file(self):
        return self.get_item_str_from_cell(row=self.row, column=2)

    def get_last_ob_file(self):
        return self.get_item_str_from_cell(row=self.row, column=3)

    def get_first_dc_file(self):
        return self.get_item_str_from_cell(row=self.row, column=4)

    def get_last_dc_file(self):
        return self.get_item_str_from_cell(row=self.row, column=5)

    def get_period(self):
        widget = self.get_widget(row=self.row, column=6)
        return widget.value()

    def get_images_per_step(self):
        widget = self.get_widget(row=self.row, column=7)
        return widget.value()

    def get_rotation(self):
        return float(self.get_item_str_from_cell(row=self.row, column=8))

    def get_fit_procedure(self):
        widget = self.get_widget(row=self.row, column=9)
        return widget.currentText()

    def get_roi(self):
        return self.get_item_str_from_cell(row=self.row, column=10)

    def get_gamma_filter_data_ob(self):
        widget = self.get_widget(row=self.row, column=11)
        return widget.currentText()

    def get_data_threshold_3x3(self):
        return int(self.get_item_str_from_cell(row=self.row, column=12))

    def get_data_threshold_5x5(self):
        return int(self.get_item_str_from_cell(row=self.row, column=13))

    def get_data_threshold_7x7(self):
        return int(self.get_item_str_from_cell(row=self.row, column=14))

    def get_data_sigma_log(self):
        return float(self.get_item_str_from_cell(row=self.row, column=15))

    def get_gamma_filter_dc(self):
        widget = self.get_widget(row=self.row, column=16)
        return widget.currentText()

    def get_dc_threshold_3x3(self):
        return int(self.get_item_str_from_cell(row=self.row, column=17))

    def get_dc_threshold_5x5(self):
        return int(self.get_item_str_from_cell(row=self.row, column=18))

    def get_dc_threshold_7x7(self):
        return int(self.get_item_str_from_cell(row=self.row, column=19))

    def get_dc_log(self):
        return float(self.get_item_str_from_cell(row=self.row, column=20))

    def get_dc_outlier_removal(self):
        widget = self.get_widget(row=self.row, column=21)
        return widget.currentText()

    def get_dc_outlier_value(self):
        return float(self.get_item_str_from_cell(row=self.row, column=22))

    def get_result_directory(self):
        return self.get_item_str_from_cell(row=self.row, column=23)

    def get_file_id(self):
        return self.get_item_str_from_cell(row=self.row, column=24)
