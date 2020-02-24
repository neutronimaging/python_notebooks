import numpy as np
import os

try:
    from PyQt4 import QtGui
except ImportError:
    from PyQt5 import QtGui

from __code._panoramic_stitching import config


class Utilities:

    def __init__(self, parent=None):
        self.parent = parent

    def get_roi_from_master_dict(self, full_file_name=''):
        master_dict = self.parent.master_dict[full_file_name]['reference_roi']
        x0 = master_dict['x0']
        y0 = master_dict['y0']
        width = master_dict['width']
        height = master_dict['height']
        return [x0, y0, width, height]

    def set_roi_to_master_dict(self, row=0, data_type='reference',
                               x0=None, y0=None, width=np.NaN, height=np.NaN):
        roi_key = "{}_roi".format(data_type)
        roi_dict = self.parent.master_dict[row][roi_key]
        if x0:
            roi_dict['x0'] = x0
            roi_dict['y0'] = y0
        roi_dict['width'] = width
        roi_dict['height'] = height

    def get_view(self, data_type='reference'):
        if data_type == 'reference':
            return self.parent.ui.reference_view
        elif data_type == 'target':
            return self.parent.ui.target_view
        else:
            return None

    def get_image(self, data_type='reference'):
        if data_type == 'reference':
            return self.get_reference_selected(key='data')
        else:
            return self.get_target_selected(key='data')

    def get_reference_selected(self, key='files'):
        row = self.get_row_selected()
        if key == 'index':
            return row
        combobox_index_selected = self.get_reference_index_selected_from_row(row=row)
        return self.parent.list_reference[key][combobox_index_selected]

    def get_target_selected(self, key='files'):
        row = self.get_reference_selected(key='index')
        combobox_index_selected = self.get_target_index_selected_from_row(row=row)
        return self.parent.list_target[key][combobox_index_selected]

    def __get_reference_file_selected(self, key='files'):
        _row_selected = self.get_row_selected()
        return self.parent.list_reference['files'][_row_selected]

    def get_row_selected(self):
        _selection = self.parent.ui.tableWidget.selectedRanges()[0]
        _row_selected = _selection.topRow()
        return _row_selected

    def get_target_index_selected_from_row(self, row=0):
        _widget = self.parent.ui.tableWidget.cellWidget(row, 1)
        return _widget.currentIndex()

    def get_reference_index_selected_from_row(self, row=0):
        _widget = self.parent.ui.tableWidget.cellWidget(row, 0)
        return _widget.currentIndex()

    def get_reference_file_selected_for_this_row(self, row=0):
        combobox_index_selected = self.get_reference_index_selected_from_row(row=row)
        return self.parent.list_reference['files'][combobox_index_selected]

    def get_target_file_selected_for_this_row(self, row=0):
        combobox_index_selected = self.get_target_index_selected_from_row(row=row)
        return self.parent.list_target['files'][combobox_index_selected]

    def set_status_of_this_row_to_message(self, row=0, message=''):
        self.parent.ui.tableWidget.item(row, 2).setText(message)

    def reset_all_status(self):
        nbr_row = self.parent.ui.tableWidget.rowCount()
        for _row in np.arange(nbr_row):
            self.set_status_of_this_row_to_message(row=_row, message="")

    def button_pressed(self, button_ui=None):
        full_file = Utilities.__make_full_file_name_to_static_folder_of(config.left_button_pressed)
        button_ui.setIcon(QtGui.QIcon(full_file))

    def button_released(self, button_ui=None):
        full_file = Utilities.__make_full_file_name_to_static_folder_of(config.left_button_released)
        button_ui.setIcon(QtGui.QIcon(full_file))


    @staticmethod
    def __make_full_file_name_to_static_folder_of(file_name):
        _file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
        full_path_file = os.path.abspath(os.path.join(_file_path, file_name))
        return full_path_file
