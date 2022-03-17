import numpy as np

from __code._utilities.table_handler import TableHandler
from __code.roi_statistics_vs_stack import StatisticsColumnIndex
from __code.roi_statistics_vs_stack.table import Table


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def recalculate_table(self):
        region = self.parent.ui.roi.getArraySlice(self.parent.live_image,
                                                  self.parent.ui.image_view.imageItem)

        x0 = region[0][0].start
        x1 = region[0][0].stop - 1
        y0 = region[0][1].start
        y1 = region[0][1].stop - 1

        y_axis_min = []
        y_axis_max = []
        y_axis_mean = []
        y_axis_median = []
        y_axis_std = []

        for _row in self.parent.data_dict.keys():
            _data = self.parent.data_dict[_row]['data']
            _data_of_roi = _data[y0: y1, x0: x1]

            _mean = np.mean(_data_of_roi)
            _max = np.max(_data_of_roi)
            _min = np.min(_data_of_roi)
            _median = np.median(_data_of_roi)
            _std = np.std(_data_of_roi)

            self.parent.data_dict[_row]['mean'] = _mean
            self.parent.data_dict[_row]['max'] = _max
            self.parent.data_dict[_row]['min'] = _min
            self.parent.data_dict[_row]['median'] = _median
            self.parent.data_dict[_row]['std'] = _std

            y_axis_min.append(_min)
            y_axis_max.append(_max)
            y_axis_mean.append(_mean)
            y_axis_median.append(_median)
            y_axis_std.append(_std)

        self.parent.y_axis['min'] = y_axis_min
        self.parent.y_axis['max'] = y_axis_max
        self.parent.y_axis['mean'] = y_axis_mean
        self.parent.y_axis['median'] = y_axis_median
        self.parent.y_axis['std'] = y_axis_std

    def update_table(self):
        data_dict = self.parent.data_dict

        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        for _row in data_dict.keys():

            _entry = data_dict[_row]
            o_table.insert_item(row=_row,
                                column=StatisticsColumnIndex.min,
                                value=_entry['min'],
                                editable=False)
            o_table.insert_item(row=_row,
                                column=StatisticsColumnIndex.max,
                                value=_entry['max'],
                                editable=False)
            o_table.insert_item(row=_row,
                                column=StatisticsColumnIndex.mean,
                                value=_entry['mean'],
                                format_str='{:0.2f}',
                                editable=False)
            o_table.insert_item(row=_row,
                                column=StatisticsColumnIndex.median,
                                value=_entry['median'],
                                format_str='{:0.2f}',
                                editable=False)
            o_table.insert_item(row=_row,
                                column=StatisticsColumnIndex.std,
                                value=_entry['std'],
                                format_str='{:0.2f}',
                                editable=False)

    def reset_table_plot(self):
        # clear table
        o_table = Table(parent=self.parent)
        o_table.reset()

        # clear plots
        self.parent.statistics_plot.axes.cla()
        self.parent.statistics_plot.draw()

        # disable menu buttons
        self.parent.ui.y_axis_groupBox.setEnabled(False)
        self.parent.ui.x_axis_groupBox.setEnabled(False)
