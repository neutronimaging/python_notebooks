from __code._utilities.table_handler import TableHandler
from __code.roi_statistics_vs_stack import StatisticsColumnIndex


class Table:

    def __init__(self, parent=None):
        self.parent = parent

    def reset(self):
        data_dict = self.parent.data_dict

        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        reset_value = "NaN"
        for _row in data_dict.keys():

            _entry = data_dict[_row]
            o_table.insert_item(row=_row,
                                column=StatisticsColumnIndex.min,
                                value=reset_value,
                                editable=False)
            o_table.insert_item(row=_row,
                                column=StatisticsColumnIndex.max,
                                value=reset_value,
                                editable=False)
            o_table.insert_item(row=_row,
                                column=StatisticsColumnIndex.mean,
                                value=reset_value,
                                editable=False)
            o_table.insert_item(row=_row,
                                column=StatisticsColumnIndex.median,
                                value=reset_value,
                                editable=False)
            o_table.insert_item(row=_row,
                                column=StatisticsColumnIndex.std,
                                value=reset_value,
                                editable=False)
