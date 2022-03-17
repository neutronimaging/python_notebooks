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
            return self.parent.x_axis['file_index']
        else:
            return self.parent.x_axis['time_offset']

    def update_statistics_plot(self):
        self.parent.statistics_plot.axes.cla()

        x_axis = self.get_x_axis()

        data_dict = self.parent.data_dict

        if self.parent.ui.mean_checkBox.isChecked():
            pass

