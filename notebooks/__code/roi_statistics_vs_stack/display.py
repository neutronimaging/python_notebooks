import numpy as np


class Display:

    def __init__(self, parent=None):
        self.parent = parent

    def update_image_view(self, slider_value=0):
        data = self.parent.data_dict[slider_value]['data']
        data = np.transpose(data)
        self.parent.ui.image_view.setImage(data)
        self.parent.live_image = data

    def get_x_axis(self):
        if self.parent.ui.file_index_radioButton.isChecked():
            return self.parent.x_axis['file_index'], 'file index'
        else:
            return self.parent.x_axis['time_offset'], 'time offset (s)'

    def update_statistics_plot(self):
        self.parent.statistics_plot.axes.cla()

        x_axis, x_axis_label = self.get_x_axis()

        nbr_plot = 0
        if self.parent.ui.mean_checkBox.isChecked():
            y_axis_mean = self.parent.y_axis['mean']
            self.parent.statistics_plot.axes.plot(x_axis, y_axis_mean, 'bv', label='mean')
            nbr_plot += 1

        if self.parent.ui.min_checkBox.isChecked():
            y_axis_mean = self.parent.y_axis['min']
            self.parent.statistics_plot.axes.plot(x_axis, y_axis_mean, 'r*', label='min')
            nbr_plot += 1

        if self.parent.ui.max_checkBox.isChecked():
            y_axis_mean = self.parent.y_axis['max']
            self.parent.statistics_plot.axes.plot(x_axis, y_axis_mean, 'r+', label='max')
            nbr_plot += 1

        if self.parent.ui.median_checkBox.isChecked():
            y_axis_mean = self.parent.y_axis['median']
            self.parent.statistics_plot.axes.plot(x_axis, y_axis_mean, 'gp', label='median')
            nbr_plot += 1

        if self.parent.ui.std_checkBox.isChecked():
            y_axis_mean = self.parent.y_axis['std']
            self.parent.statistics_plot.axes.plot(x_axis, y_axis_mean, 'cx', label='std')
            nbr_plot += 1

        if nbr_plot > 0:
            self.parent.statistics_plot.axes.legend()

        self.parent.statistics_plot.axes.set_xlabel(x_axis_label)
        self.parent.statistics_plot.axes.set_ylabel("counts")

        self.parent.statistics_plot.draw()
