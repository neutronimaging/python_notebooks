import numpy as np

from NeuNorm.normalization import Normalization

from __code._utilities.table_handler import TableHandler
from __code.outliers_filtering.display import Display
from __code.outliers_filtering.algorithm import Algorithm


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def algorithm_changed(self):
        high_intensity_status = self.parent.ui.fix_high_intensity_counts_checkBox.isChecked()
        self.parent.ui.median_thresholding_frame.setEnabled(high_intensity_status)
        self.table_selection_changed()

    def table_selection_changed(self):
        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        row_selected = o_table.get_row_selected()
        short_file_name = self.parent.list_short_file_name[row_selected]
        if self.parent.data.get(short_file_name, None) is None:
            self.parent.data[short_file_name] = {'raw': self.load_raw_data(row=row_selected),
                                                 'filtered': None}

        if self.parent.image_size is None:
            [height, width] = np.shape(self.parent.data[short_file_name]['raw'])
            self.parent.image_size = [height, width]

        o_display = Display(parent=self.parent)
        filtered_data = self.calculate_filtered_data(raw_data=self.parent.data[short_file_name]['raw'])
        self.parent.data[short_file_name]['filtered'] = filtered_data
        o_display.filtered_image(data=filtered_data)
        o_display.raw_image(data=self.parent.data[short_file_name]['raw'])


    def load_raw_data(self, row=0):
        file = self.parent.list_files[row]
        o_norm = Normalization()
        o_norm.load(file=file, auto_gamma_filter=False,
                    manual_gamma_filter=False)
        _raw_data = np.squeeze(o_norm.data['sample']['data'])
        return _raw_data

    def calculate_filtered_data(self, raw_data=None):

        o_algo = Algorithm(parent=self.parent,
                           data=raw_data)
        o_algo.run()

        return o_algo.get_processed_data()
