import numpy as np
import os
import collections
from PIL import Image


class Get:

    def __init__(self, parent=None):
        self.parent = parent

    def metadata_column_selected(self):
        selection = self.parent.ui.tableWidget.selectedRanges()[0]
        return selection.leftColumn()

    def get_y_axis_data(self):
        y_axis_column_index = self.parent.y_axis_column_index
        y_axis = self.get_axis_data(axis_index=y_axis_column_index)
        return y_axis

    def get_x_axis_data(self):
        x_axis_column_index = self.parent.x_axis_column_index
        x_axis = self.get_axis_data(axis_index=x_axis_column_index)
        return x_axis

    def get_axis_data(self, axis_index=0):
        nbr_row = self.parent.ui.tableWidget.rowCount()
        axis_data = []
        for _row in np.arange(nbr_row):
            _row_str = str(self.parent.ui.tableWidget.item(_row, axis_index).text())
            axis_data.append(_row_str)
        return axis_data

    def metadata_column(self):
        data = []
        nbr_row = self.parent.ui.tableWidget.rowCount()
        for _row in np.arange(nbr_row):
            _row_str = str(self.parent.ui.tableWidget.item(_row, 1).text())
            split_row_str = _row_str.split(":")
            if len(split_row_str) == 1:
                _row_str = split_row_str[0]
            else:
                _row_str = split_row_str[1]
            try:
                _row_value = np.float(_row_str)
            except:
                self.parent.ui.statusbar.showMessage("Error Displaying Metadata Graph!", 10000)
                self.parent.ui.statusbar.setStyleSheet("color: red")
                return []

            data.append(_row_value)

        return data

    def metadata_text(self, metadata_index=1):
        """return the text and value of the metadata to display"""

        if metadata_index == 1:
            metadata_name = str(self.parent.ui.prefix_lineEdit_1.text())
            metadata_units = str(self.parent.ui.suffix_lineEdit_1.text())
        else:
            metadata_name = str(self.parent.ui.prefix_lineEdit_2.text())
            metadata_units = str(self.parent.ui.suffix_lineEdit_2.text())

        slider_index = self.parent.ui.file_slider.value()

        index_of_y_axis = self.parent.y_axis_column_index
        metadata_value = str(self.parent.ui.tableWidget.item(slider_index, index_of_y_axis).text())
        if metadata_name.strip() == '':
            return "{} {}".format(metadata_value, metadata_units)
        else:
            return "{}: {} {}".format(metadata_name, metadata_value, metadata_units)

    def scale_legend(self):
        real_scale_value = str(self.parent.ui.scale_real_size.text())
        units_index_selected = self.parent.ui.scale_units_combobox.currentIndex()
        html_units = self.parent.list_scale_units['html'][units_index_selected]
        return "{} {}".format(real_scale_value, html_units)

    def raw_metadata_column(self):
        data = []
        nbr_row = self.parent.ui.tableWidget.rowCount()
        for _row in np.arange(nbr_row):
            _row_str = str(self.parent.ui.tableWidget.item(_row, 1).text())
            data.append(_row_str)
        return data

    def color(self, color_type='html', source='metadata'):
        if source == 'metadata':
            color_selected = self.parent.ui.metadata_color_combobox.currentText().lower()
        elif source == 'graph':
            color_selected = self.parent.ui.graph_color_combobox.currentText().lower()
        else:
            color_selected = self.parent.ui.scale_color_combobox.currentText().lower()

        if color_type == 'html':
            return self.parent.html_color[color_selected]
        elif color_type == 'rgba':
            return self.parent.rgba_color[color_selected]
        else:
            return self.parent.rgb_color[color_selected]

    def list_metadata(self):
        first_file = self.parent.data_dict['file_name'][0]
        dict_list_metadata = collections.OrderedDict()
        [_, ext] = os.path.splitext(os.path.basename(first_file))
        if ext in [".tif", ".tiff"]:
            o_image0 = Image.open(first_file)
            info = collections.OrderedDict(sorted(o_image0.tag_v2.items()))
            list_metadata = []
            list_key = []
            for tag, value in info.items():
                dict_list_metadata[tag] = value
                list_metadata.append("{} -> {}".format(tag, value))
                list_key.append(tag)
            self.parent.list_metadata = list_key
            self.parent.dict_list_metadata = dict_list_metadata
            return list_metadata
        else:
            return []
