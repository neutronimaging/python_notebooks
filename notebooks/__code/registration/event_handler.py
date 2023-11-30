from qtpy.QtWidgets import QMenu
from qtpy import QtGui
import numpy as np
import os
from skimage import transform
from scipy.ndimage.interpolation import shift

from __code._utilities.table_handler import TableHandler
from __code._utilities.check import is_float
from __code.registration.calculate import Calculate


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def table_right_click(self):

        top_menu = QMenu(self.parent)

        state_of_paste = True
        if self.parent.value_to_copy is None:
            state_of_paste = False

        copy_menu = QMenu("Copy ...")
        top_menu.addMenu(copy_menu)
        copy_xoffset_menu = copy_menu.addAction("From first xoffset cell selected")
        copy_yoffset_menu = copy_menu.addAction("From first yoffset cell selected")

        paste_menu = QMenu("Paste ...")
        paste_menu.setEnabled(state_of_paste)
        top_menu.addMenu(paste_menu)
        paste_xoffset_menu = paste_menu.addAction("In all xoffset cell selected")
        paste_yoffset_menu = paste_menu.addAction("In all yoffset cell selected")

        action = top_menu.exec_(QtGui.QCursor.pos())

        if action == copy_xoffset_menu:
            self.copy_xoffset_value()
        elif action == copy_yoffset_menu:
            self.copy_yoffset_value()
        elif action == paste_xoffset_menu:
            self.paste_xoffset_value()
        elif action == paste_yoffset_menu:
            self.paste_yoffset_value()

    def copy_xoffset_value(self):
        self.parent.value_to_copy = self.get_value_to_copy(column=1)

    def copy_yoffset_value(self):
        self.parent.value_to_copy = self.get_value_to_copy(column=2)

    def get_value_to_copy(self, column=1):
        o_table = TableHandler(self.parent.ui.tableWidget)
        row_selected = o_table.get_row_selected()
        value_to_copy = o_table.get_item_str_from_cell(row=row_selected,
                                                       column=column)
        return value_to_copy

    def paste_xoffset_value(self):
        self.paste_value_copied(column=1)

    def paste_yoffset_value(self):
        self.paste_value_copied(column=2)

    def paste_value_copied(self, column=1):
        o_table = TableHandler(self.parent.ui.tableWidget)
        row_selected = o_table.get_rows_of_table_selected()
        self.parent.ui.tableWidget.blockSignals(True)

        for _row in row_selected:
            o_table.set_item_with_str(row=_row,
                                      column=column,
                                      cell_str=self.parent.value_to_copy)

        self.parent.ui.tableWidget.blockSignals(False)

    def update_table_according_to_filter(self):
        filter_flag = self.parent.ui.filter_radioButton.isChecked()
    
        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
    
        def should_row_be_visible(row_value=None, filter_algo_selected="<=", filter_value=None):
    
            if is_float(filter_value):
                o_table.set_all_row_hidden(False)
                return
    
            if filter_algo_selected == "<=":
                return float(row_value) <= float(filter_value)
            elif filter_algo_selected == ">=":
                return float(row_value) >= float(filter_value)
            else:
                raise NotImplementedError("algo not implemented!")
    
        if filter_flag:
            # select only rows according to filter
            filter_column_selected = self.parent.ui.filter_column_name_comboBox.currentText()
            filter_algo_selected = self.parent.ui.filter_logic_comboBox.currentText()
            filter_value = self.parent.ui.filter_value.text()
    
            if filter_column_selected == "Xoffset":
                filter_column_index = 1
            elif filter_column_selected == "Yoffset":
                filter_column_index = 2
            elif filter_column_selected == "Rotation":
                filter_column_index = 3
            else:
                raise NotImplementedError("column can not be used with filter!")
    
            nbr_row = o_table.row_count()
            for _row in np.arange(nbr_row):
                _row_value = float(o_table.get_item_str_from_cell(row=_row, column=filter_column_index))
                _should_row_be_visible = should_row_be_visible(row_value=_row_value,
                                                               filter_algo_selected=filter_algo_selected,
                                                               filter_value=filter_value)
                o_table.set_row_hidden(_row, not _should_row_be_visible)
        else:
            # all rows are visible
            o_table.set_all_row_hidden(False)

    def close_all_markers(self):
        for marker in self.parent.markers_table.keys():
            self.close_markers_of_tab(marker_name=marker)

    def close_markers_of_tab(self, marker_name=''):
        """remove box and label (if they are there) of each marker"""
        _data = self.parent.markers_table[marker_name]['data']
        for _file in _data:
            _marker_ui = _data[_file]['marker_ui']
            if _marker_ui:
                self.parent.ui.image_view.removeItem(_marker_ui)

            _label_ui = _data[_file]['label_ui']
            if _label_ui:
                self.parent.ui.image_view.removeItem(_label_ui)

    def profile_line_moved(self):
        """update profile plot"""
        if self.parent.live_image is None:
            return

        self.parent.ui.profile.clear()
        # try:
        #     self.parent.ui.profile.scene().removeItem(self.parent.legend)
        # except Exception as e:
        #     pass

        self.parent.legend = self.parent.ui.profile.addLegend()

        region = self.parent.ui.profile_line.getArraySlice(self.parent.live_image,
                                                           self.parent.ui.image_view.imageItem)

        x0 = region[0][0].start + 3
        x1 = region[0][0].stop - 3
        y0 = region[0][1].start + 3
        y1 = region[0][1].stop - 3

        p1 = [x0, y0]
        p2 = [x1, y1]

        intermediate_points = Calculate.intermediates_points(p1, p2)
        xaxis = np.arange(len(intermediate_points))

        # profiles selected
        # if only one row selected !
        if self.parent.ui.selection_groupBox.isVisible():

            if self.parent.ui.selection_all.isChecked():
                min_row = int(self.parent.ui.opacity_selection_slider.minimum() / 100)
                max_row = int(self.parent.ui.opacity_selection_slider.maximum() / 100)

                for _index in np.arange(min_row, max_row + 1):
                    if _index == self.parent.reference_image_index:
                        continue

                    _data = np.transpose(self.parent.data_dict['data'][_index])
                    _filename = os.path.basename(self.parent.data_dict['file_name'][_index])
                    _profile = [_data[_point[0], _point[1]] for _point in intermediate_points]
                    self.parent.ui.profile.plot(xaxis, _profile,
                                                name=_filename,
                                                pen=self.parent.list_rgb_profile_color[_index])

            else:  # selection slider
                slider_index = self.parent.ui.opacity_selection_slider.sliderPosition() / 100
                from_index = int(slider_index)
                _data = np.transpose(self.parent.data_dict['data'][from_index])
                _filename = os.path.basename(self.parent.data_dict['file_name'][from_index])
                _profile = [_data[_point[0], _point[1]] for _point in intermediate_points]
                self.parent.ui.profile.plot(xaxis,
                                           _profile,
                                           name=_filename,
                                           pen=self.parent.list_rgb_profile_color[from_index])

                if from_index == slider_index:
                    pass

                else:
                    to_index = int(slider_index + 1)
                    _data = np.transpose(self.parent.data_dict['data'][to_index])
                    _filename = os.path.basename(self.parent.data_dict['file_name'][to_index])
                    _profile = [_data[_point[0], _point[1]] for _point in intermediate_points]
                    self.parent.ui.profile.plot(xaxis,
                                                _profile,
                                                name=_filename,
                                                pen=self.parent.list_rgb_profile_color[to_index])

        else:

            table_selection = self.parent.ui.tableWidget.selectedRanges()
            if not (table_selection is None):

                table_selection = table_selection[0]
                row_selected = table_selection.topRow()

                if not row_selected == self.parent.reference_image_index:
                    _data = np.transpose(self.parent.data_dict['data'][row_selected])
                    _filename = os.path.basename(self.parent.data_dict['file_name'][row_selected])
                    _profile = [_data[_point[0], _point[1]] for _point in intermediate_points]
                    self.parent.ui.profile.plot(xaxis,
                                                _profile,
                                                name=_filename,
                                                pen=self.parent.list_rgb_profile_color[row_selected])

        # selected_image = self.parent.live_image
        # profile_selected = [selected_image[_point[0],
        #                                    _point[1]] for _point in intermediate_points]
        #
        # self.parent.ui.profile.plot(xaxis, profile_selected, name='Selected Image')

        # Always display profile reference
        reference_image = np.transpose(self.parent.reference_image)
        profile_reference = [reference_image[_point[0],
                                             _point[1]] for _point in intermediate_points]

        reference_file_name = os.path.basename(self.parent.data_dict['file_name'][self.parent.reference_image_index])
        self.parent.ui.profile.plot(xaxis, profile_reference,
                                    pen=self.parent.color_reference_profile,
                                    name='Ref.: {}'.format(reference_file_name))

    def modified_images(self, list_row=[], all_row=False):
        """using data_dict_raw images, will apply offset and rotation parameters
        and will save them in data_dict for plotting"""

        data_raw = self.parent.data_dict_raw['data'].copy()

        if all_row:
            list_row = np.arange(0, self.parent.nbr_files)
        else:
            list_row = list_row

        for _row in list_row:

            try:
                xoffset = int(float(self.parent.ui.tableWidget.item(_row, 1).text()))
                yoffset = int(float(self.parent.ui.tableWidget.item(_row, 2).text()))
                rotate_angle = float(self.parent.ui.tableWidget.item(_row, 3).text())
            except AttributeError:
                return

            _data = data_raw[_row].copy()
            _data = transform.rotate(_data, rotate_angle)
            _data = shift(_data, (yoffset, xoffset), )

            self.parent.data_dict['data'][_row] = _data
