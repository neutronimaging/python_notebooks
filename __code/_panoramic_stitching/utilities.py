import numpy as np


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

    def set_roi_to_master_dict(self, master_dict_key=None, data_type='reference',
                               x0=None, y0=None, width=np.NaN, height=np.NaN):
        roi_key = "{}_roi".format(data_type)
        roi_dict = self.parent.master_dict[master_dict_key][roi_key]
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
        _row_selected = self.__get_reference_index_selected()
        if key == 'index':
            return _row_selected
        return self.parent.list_reference[key][_row_selected]

    def get_target_selected(self, key='files'):
        row = self.get_reference_selected(key='index')
        combobox_index_selected = self.get_target_index_selected_from_row(row=row)
        return self.parent.list_target[key][combobox_index_selected]

    def __get_reference_file_selected(self, key='files'):
        _row_selected = self.__get_reference_index_selected()
        return self.parent.list_reference['files'][_row_selected]

    def __get_reference_index_selected(self):
        _selection = self.parent.ui.tableWidget.selectedRanges()[0]
        _row_selected = _selection.topRow()
        return _row_selected

    def get_target_index_selected_from_row(self, row=0):
        _widget = self.parent.ui.tableWidget.cellWidget(row, 1)
        return _widget.currentIndex()

    # def get_target_file_selected(self):
    #     row = self.get_reference_file_selected()
    #     combobox_index_selected = self.get_target_index_selected_from_row(row=row)
    #     return self.parent.list_target['files'][combobox_index_selected]
