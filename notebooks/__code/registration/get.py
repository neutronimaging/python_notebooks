import numpy as np
import os


class Get:

    def __init__(self, parent=None):
        self.parent = parent

    def list_short_file_selected(self):
        self.get_list_short_file_selected()

    def get_list_short_file_selected(self):
        list_row_selected = self.get_list_row_selected()
        full_list_files = np.array(self.parent.data_dict['file_name'])
        list_file_selected = full_list_files[list_row_selected]
        list_short_file_selected = [os.path.basename(_file) for _file in
                                    list_file_selected]
        return list_short_file_selected

    def list_row_selected(self):
        table_selection = self.parent.ui.tableWidget.selectedRanges()

        # that means we selected the first row
        if table_selection is None:
            return [0]

        table_selection = table_selection[0]
        top_row = table_selection.topRow()
        bottom_row = table_selection.bottomRow() + 1

        return np.arange(top_row, bottom_row)

    def image_selected(self):
        """to get the image selected, we will use the table selection as the new version
        allows several rows"""
        # index_selected = self.ui.file_slider.value()

        table_selection = self.parent.ui.tableWidget.selectedRanges()
        if table_selection is None:
            return []

        table_selection = table_selection[0]
        top_row = table_selection.topRow()  # offset because first image is reference image
        bottom_row = table_selection.bottomRow() + 1

        _image = np.mean(self.parent.data_dict['data'][top_row:bottom_row], axis=0)
        return _image
