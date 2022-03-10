from NeuNorm.normalization import Normalization

from __code._utilities.table_handler import TableHandler
from __code.gamma_filtering.display import Display


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def algorithm_changed(self):
        hard_status = self.parent.ui.hard_thresholding_radioButton.isChecked()
        self.parent.ui.hard_thresholding_frame.setEnabled(hard_status)

        median_status = self.parent.ui.median_thresholding_radioButton.isChecked()
        self.parent.ui.median_thresholding_frame.setEnabled(median_status)

    def table_selection_changed(self):
        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        row_selected = o_table.get_row_selected()
        short_file_name = self.parent.list_short_file_name[row_selected]
        if self.parent.data.get(short_file_name, None) is None:
            self.parent.data[short_file_name] = {'raw': self.load_raw_data(row=row_selected),
                                                 'filtered': None}

        o_display = Display(parent=self.parent)
        o_display.raw_image(data=self.parent.data[short_file_name]['raw'])

    def load_raw_data(self, row=0):
        file = self.parent.list_files[row]
        o_norm = Normalization()
        o_norm.load(file=file, auto_gamma_filter=False,
                    manual_gamma_filter=False)
        _raw_data = o_norm.data['sample']['data']
        return _raw_data
