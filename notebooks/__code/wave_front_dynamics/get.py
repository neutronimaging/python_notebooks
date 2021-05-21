from __code._utilities.parent import Parent


class Get(Parent):

    def prepare_data_bin_size(self):
        return self.parent.ui.bin_value_horizontalSlider.value()

    def prepare_data_file_index(self):
        return self.parent.ui.file_index_horizontalSlider.value()

    def prepare_data_bin_type(self):
        if self.parent.ui.prepare_data_bin_type_mean.isChecked():
            return 'mean'
        elif self.parent.ui.prepare_data_bin_type_median.isChecked():
            return 'median'
        else:
            raise NotImplementedError("data bin type not implemented!")
