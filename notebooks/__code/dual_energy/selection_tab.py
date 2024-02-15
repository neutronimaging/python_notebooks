import numpy as np
import pyqtgraph as pg
from qtpy import QtGui
from collections import OrderedDict
from qtpy.QtWidgets import QFileDialog
from pathlib import Path
import os

from NeuNorm.normalization import Normalization

from __code._utilities.array import check_size
from __code.dual_energy.get import Get
from __code.utilities import find_nearest_index
from __code.table_handler import TableHandler


class SelectionTab:
    background_color_of_max_bin_ratio = QtGui.QColor(107, 255, 157)

    def __init__(self, parent=None):
        self.parent = parent

    def update_selection_profile_plot(self):
        o_get = Get(parent=self.parent)
        x_axis, x_axis_label = o_get.x_axis()
        self.parent.ui.profile.clear()

        # large selection region
        [x0, y0, x1, y1, _, _] = o_get.selection_roi_dimension()
        profile = o_get.profile_of_roi(x0, y0, x1, y1)
        self.parent.roi_selection_dict = {'x0': x0,
                                          'y0': y0,
                                          'x1': x1,
                                          'y1': y1}
        x_axis, y_axis = check_size(x_axis=x_axis,
                                    y_axis=profile)
        self.parent.ui.profile.plot(x_axis, y_axis, pen=(self.parent.selection_roi_rgb[0],
                                                         self.parent.selection_roi_rgb[1],
                                                         self.parent.selection_roi_rgb[2]))

        self.parent.ui.profile.setLabel("bottom", x_axis_label)
        self.parent.ui.profile.setLabel("left", 'Mean transmission')

        # vertical line showing peak to fit
        profile_selection_range = [x_axis[self.parent.profile_selection_range[0]],
                                   x_axis[self.parent.profile_selection_range[1]]]

        self.parent.profile_selection_range_ui = pg.LinearRegionItem(values=profile_selection_range,
                                                                     orientation=None,
                                                                     brush=None,
                                                                     movable=True,
                                                                     bounds=None)
        self.parent.profile_selection_range_ui.sigRegionChanged.connect(self.parent.profile_selection_range_changed)
        self.parent.profile_selection_range_ui.sigRegionChangeFinished.connect(
                self.parent.roi_moved)
        self.parent.profile_selection_range_ui.setZValue(-10)
        self.parent.ui.profile.addItem(self.parent.profile_selection_range_ui)

        _pen = QtGui.QPen()
        _pen.setColor(self.parent.bin_line_settings['color'])
        _pen.setWidthF(self.parent.bin_line_settings['width'])

        if self.parent.list_bin_ui:
            for _bin_ui in self.parent.list_bin_ui:
                self.parent.ui.profile.removeItem(_bin_ui)
            self.parent.list_bin_ui = []

        if self.parent.list_bin_positions:
            current_axis_name = o_get.x_axis_name_checked()
            for bin in self.parent.list_bin_positions[current_axis_name]:
                if current_axis_name == 'tof':
                    bin *= 1e6
                _bin_ui = pg.InfiniteLine(bin,
                                          movable=False,
                                          pen=_pen)
                self.parent.ui.profile.addItem(_bin_ui)
                self.parent.list_bin_ui.append(bin)

    def update_bin_size_widgets(self):
        o_get = Get(parent=self.parent)
        x_axis_units = o_get.x_axis_units()
        current_axis_name = o_get.x_axis_name_checked()

        # update units
        self.parent.ui.selection_bin_size_units.setText(x_axis_units)

        bin_size_value = self.parent.bin_size_value[current_axis_name]
        if current_axis_name == 'tof':
            bin_size_value *= 1e6
        elif current_axis_name == 'lambda':
            bin_size_value = "{:2f}".format(bin_size_value)
        self.parent.ui.selection_bin_size_value.setText(str(bin_size_value))

    def calculate_bin_size_in_all_units(self):
        current_value = float(self.parent.ui.selection_bin_size_value.text())
        o_get = Get(parent=self.parent)
        current_axis_name = o_get.x_axis_name_checked()

        tof_array_s = self.parent.tof_array_s
        lambda_array = self.parent.lambda_array

        if current_axis_name == 'index':
            current_value = int(current_value)
            bin_index = current_value
            bin_tof = tof_array_s[current_value]
            bin_lambda = lambda_array[current_value]
        elif current_axis_name == 'tof':
            bin_index = find_nearest_index(array=tof_array_s,
                                           value=current_value * 1e-6)
            bin_tof = current_value
            bin_lambda = lambda_array[bin_index]
        elif current_axis_name == 'lambda':
            bin_index = find_nearest_index(array=lambda_array,
                                           value=current_value)
            bin_tof = tof_array_s[bin_index]
            bin_lambda = current_value

        self.parent.bin_size_value = {'index' : bin_index,
                                      'tof'   : bin_tof,
                                      'lambda': bin_lambda}

    def make_list_of_bins(self):
        [from_index, to_index] = self.parent.profile_selection_range

        list_bin = {'index' : [],
                    'tof'   : [],
                    'lambda': []}

        # index scale
        index_bin_size = self.parent.bin_size_value['index']
        left_bin_value = from_index
        right_bin_value = from_index + index_bin_size
        list_bin['index'] = [left_bin_value]
        while right_bin_value <= to_index:
            list_bin['index'].append(right_bin_value)
            right_bin_value += index_bin_size

        # tof scale
        tof_array_s = self.parent.tof_array_s
        list_bin['tof'] = tof_array_s[list_bin['index']]

        # lambda scale
        lambda_array = self.parent.lambda_array
        list_bin['lambda'] = lambda_array[list_bin['index']]

        self.parent.list_bin_positions = list_bin

    def update_all_size_widgets_infos(self):

        if self.parent.ui.square_roi_radiobutton.isChecked():
            return

        roi_id = self.parent.roi_id
        region = roi_id.getArraySlice(self.parent.final_image,
                                      self.parent.ui.image_view.imageItem)
        x0 = region[0][0].start
        x1 = region[0][0].stop
        y0 = region[0][1].start
        y1 = region[0][1].stop

        new_width = x1 - x0 - 1
        new_height = y1 - y0 - 1

        # if new width and height is the same as before, just skip that step
        if self.parent.new_dimensions_within_error_range():
            return

        self.parent.ui.roi_width.setText(str(new_width))
        self.parent.ui.roi_height.setText(str(new_height))
        self.parent.ui.profile_of_bin_size_width.setText(str(new_width))
        self.parent.ui.profile_of_bin_size_height.setText(str(new_height))

        max_value = np.min([new_width, new_height])
        self.parent.ui.profile_of_bin_size_slider.setValue(max_value)
        self.parent.ui.profile_of_bin_size_slider.setMaximum(max_value)

    # def get_shrinking_roi_dimension(self):
    # 	coordinates = self.get_coordinates_of_new_inside_selection_box()
    # 	return [coordinates['x0'],
    # 	        coordinates['y0'],
    # 	        coordinates['x0'] + coordinates['width'],
    # 	        coordinates['y0'] + coordinates['height']]

    # def get_coordinates_of_new_inside_selection_box(self):
    # 	# retrieve x0, y0, width and height of full selection
    # 	region = self.parent.roi_id.getArraySlice(self.parent.final_image, self.parent.ui.image_view.imageItem)
    # 	x0 = region[0][0].start
    # 	y0 = region[0][1].start
    # 	# [x0, y0] = self.parentselection_x0y0
    # 	width_full_selection = int(str(self.parent.ui.roi_width.text()))
    # 	height_full_selection = int(str(self.parent.ui.roi_height.text()))
    #
    # 	delta_width = width_full_selection - width_requested
    # 	delta_height = height_full_selection - height_requested
    #
    # 	new_x0 = x0 + int(delta_width / 2)
    # 	new_y0 = y0 + int(delta_height / 2)
    #
    # 	return {'x0'   : new_x0, 'y0': new_y0,
    # 	        'x1'   : new_x0 + width_requested + 1, 'y1': new_y0 + height_requested + 1,
    # 	        'width': width_requested, 'height': height_requested}

    def update_selection(self, new_value=None, mode='square'):
        if self.parent.roi_id is None:
            return

        try:
            region = self.parent.roi_id.getArraySlice(self.parent.final_image,
                                                      self.parent.ui.image_view.imageItem)
        except TypeError:
            return

        x0 = region[0][0].start
        y0 = region[0][1].start
        self.parent.selection_x0y0 = [x0, y0]

        # remove old one
        self.parent.ui.image_view.removeItem(self.parent.roi_id)

        _pen = QtGui.QPen()
        _pen.setColor(self.parent.roi_settings['color'])
        _pen.setWidthF(self.parent.roi_settings['width'])
        self.parent.roi_id = pg.ROI([x0, y0],
                                    [new_value, new_value],
                                    pen=_pen,
                                    scaleSnap=True)

        self.parent.ui.image_view.addItem(self.parent.roi_id)
        self.parent.roi_id.sigRegionChanged.connect(self.parent.roi_moved)

        if mode == 'square':
            self.parent.ui.roi_width.setText(str(new_value))
            self.parent.ui.roi_height.setText(str(new_value))
            self.parent.reset_profile_of_bin_size_slider()
            self.parent.update_profile_of_bin_size_infos()
        else:
            self.parent.roi_id.addScaleHandle([1, 1], [0, 0])

        self.update_selection_profile_plot()
        self.update_roi_defined_by_profile_of_bin_size_slider()

    def update_selection_plot(self):
        self.parent.ui.profile.clear()
        o_get = Get(parent=self.parent)
        x_axis, x_axis_label = o_get.x_axis()
        max_value = self.parent.ui.profile_of_bin_size_slider.maximum()
        roi_selected = max_value - self.parent.ui.profile_of_bin_size_slider.value()

        y_axis = self.parent.fitting_input_dictionary['rois'][roi_selected]['profile']

        self.parent.ui.profile.plot(x_axis, y_axis, pen=(self.parent.shrinking_roi_rgb[0],
                                                         self.parent.shrinking_roi_rgb[1],
                                                         self.parent.shrinking_roi_rgb[2]))
        self.parent.ui.profile.setLabel("bottom", x_axis_label)
        self.parent.ui.profile.setLabel("left", 'Mean transmission')

        # full region
        y_axis = self.parent.fitting_input_dictionary['rois'][0]['profile']
        self.parent.ui.profile.plot(x_axis, y_axis, pen=(self.parent.selection_roi_rgb[0],
                                                         self.parent.selection_roi_rgb[1],
                                                         self.parent.selection_roi_rgb[2]))

    def profile_of_bin_size_slider_changed(self, new_value):
        try:
            self.parent.update_dict_profile_to_fit()
            if self.parent.ui.square_roi_radiobutton.isChecked():
                new_width = new_value
                new_height = new_value
            else:
                initial_roi_width = int(str(self.parent.ui.roi_width.text()))
                initial_roi_height = int(str(self.parent.ui.roi_height.text()))
                if initial_roi_width == initial_roi_height:
                    new_width = new_value
                    new_height = new_value
                elif initial_roi_width < initial_roi_height:
                    new_width = new_value
                    delta = initial_roi_width - new_width
                    new_height = initial_roi_height - delta
                else:
                    new_height = new_value
                    delta = initial_roi_height - new_height
                    new_width = initial_roi_width - delta

            self.parent.ui.profile_of_bin_size_width.setText(str(new_width))
            self.parent.ui.profile_of_bin_size_height.setText(str(new_height))
            self.update_roi_defined_by_profile_of_bin_size_slider()
            self.update_selection_profile_plot()
        except AttributeError:
            pass

    def update_roi_defined_by_profile_of_bin_size_slider(self):
        coordinates_new_selection = self.get_coordinates_of_new_inside_selection_box()
        self.parent.shrinking_roi = coordinates_new_selection
        x0 = coordinates_new_selection['x0']
        y0 = coordinates_new_selection['y0']
        width = coordinates_new_selection['width']
        height = coordinates_new_selection['height']

        # remove old selection
        if self.parent.shrinking_roi_id:
            self.parent.ui.image_view.removeItem(self.parent.shrinking_roi_id)

        # plot new box
        _pen = QtGui.QPen()
        _pen.setDashPattern(self.parent.shrinking_roi_settings['dashes_pattern'])
        _pen.setColor(self.parent.shrinking_roi_settings['color'])
        _pen.setWidthF(self.parent.shrinking_roi_settings['width'])

        self.parent.shrinking_roi_id = pg.ROI([x0, y0],
                                              [width, height],
                                              pen=_pen,
                                              scaleSnap=True,
                                              movable=False)
        self.parent.ui.image_view.addItem(self.parent.shrinking_roi_id)

    def update_profile_of_bin_slider_widget(self):
        self.parent.change_profile_of_bin_slider_signal()
        fitting_input_dictionary = self.parent.fitting_input_dictionary
        dict_rois_imported = OrderedDict()
        nbr_key = len(fitting_input_dictionary['rois'].keys())
        for _index, _key in enumerate(fitting_input_dictionary['rois'].keys()):
            dict_rois_imported[nbr_key - 1 - _index] = {'width' : fitting_input_dictionary['rois'][_key]['width'],
                                                        'height': fitting_input_dictionary['rois'][_key]['height']}
        self.parent.dict_rois_imported = dict_rois_imported
        self.parent.ui.profile_of_bin_size_slider.setRange(0, len(dict_rois_imported) - 1)
        # self.parent.ui.profile_of_bin_size_slider.setMinimum(0)
        # self.parent.ui.profile_of_bin_size_slider.setMaximum(len(dict_rois_imported)-1)
        self.parent.ui.profile_of_bin_size_slider.setSingleStep(1)
        self.parent.ui.profile_of_bin_size_slider.setValue(len(dict_rois_imported) - 1)
        self.parent.update_profile_of_bin_slider_labels()

    def update_selection_roi_slider_changed(self):
        value = self.parent.ui.roi_size_slider.value()
        self.parent.selection_roi_slider_changed(value)

    def calculate_big_table(self):
        list_data = self.parent.o_norm.data['sample']['data']
        list_bin_positions = self.parent.list_bin_positions
        list_bin_index = list_bin_positions['index']
        nbr_bin = len(list_bin_index) - 1
        x0 = self.parent.roi_selection_dict['x0']
        y0 = self.parent.roi_selection_dict['y0']
        x1 = self.parent.roi_selection_dict['x1']
        y1 = self.parent.roi_selection_dict['y1']

        self.initialize_table(nbr_bin=nbr_bin)

        # calculate the mean of current bin and current ROI
        list_mean_counts_of_bin = []
        for n_bin in np.arange(nbr_bin):
            left_bin = list_bin_index[n_bin]
            right_bin = list_bin_index[n_bin + 1]
            mean_images_of_bin = np.nanmean(list_data[left_bin:right_bin][:][:], axis=0)
            mean_images_of_bin_and_selection = np.nanmean(mean_images_of_bin[y0:y1, x0:x1])
            list_mean_counts_of_bin.append(mean_images_of_bin_and_selection)

        o_table = TableHandler(table_ui=self.parent.ui.calculation_bin_table)
        max_ratio_value = 0
        row_and_column_of_max_ratio_value = {'row'   : [],
                                             'column': []}
        for _row in np.arange(nbr_bin):
            for _col in np.arange(_row, nbr_bin):
                bin_col_divided_by_bin_row = list_mean_counts_of_bin[_col] / list_mean_counts_of_bin[_row]
                diff_with_1 = np.abs(1 - bin_col_divided_by_bin_row)
                if diff_with_1 > max_ratio_value:
                    max_ratio_value = diff_with_1
                    row_and_column_of_max_ratio_value['row'] = [_row]
                    row_and_column_of_max_ratio_value['column'] = [_col]
                elif diff_with_1 == max_ratio_value:
                    row_and_column_of_max_ratio_value['row'].append(_row)
                    row_and_column_of_max_ratio_value['column'].append(_col)

                # choose to display the difference related to 1
                diff_from_1 = np.abs(1 - bin_col_divided_by_bin_row)
                _item = o_table.insert_item_with_float(row=_row,
                                                       column=_col,
                                                       float_value=diff_from_1,
                                                       format_str="{:.4f}")

        # change the background of the max_ratio_value_cell
        for _row, _col in zip(row_and_column_of_max_ratio_value['row'],
                              row_and_column_of_max_ratio_value['column']):
            o_table.set_background_color(row=_row,
                                         column=_col,
                                         qcolor=self.background_color_of_max_bin_ratio)

        self.fill_summary_table(bin_index_1=row_and_column_of_max_ratio_value['row'][0],
                                bin_index_2=row_and_column_of_max_ratio_value['column'][0])

        self.parent.optimum_bin_ratio = {'bin_number_1': row_and_column_of_max_ratio_value['row'][0],
                                         'bin_number_2': row_and_column_of_max_ratio_value['column'][0]}

    @staticmethod
    def get_file_index_range(bin_index=None, list_bin_positions=None):
        return SelectionTab.get_range_for_given_key(key='index',
                                                    index=bin_index,
                                                    list_bin_positions=list_bin_positions)

    @staticmethod
    def get_tof_index_range(bin_index=None, list_bin_positions=None):
        return SelectionTab.get_range_for_given_key(key='tof',
                                                    index=bin_index,
                                                    list_bin_positions=list_bin_positions)

    @staticmethod
    def get_lambda_index_range(bin_index=None, list_bin_positions=None):
        return SelectionTab.get_range_for_given_key(key='lambda',
                                                    index=bin_index,
                                                    list_bin_positions=list_bin_positions)

    @staticmethod
    def get_range_for_given_key(key='index', index=0, list_bin_positions=None):
        from_index = list_bin_positions[key][index]
        to_index = list_bin_positions[key][index + 1]
        return (from_index, to_index)

    def fill_summary_table(self, bin_index_1=None, bin_index_2=None):
        o_table = TableHandler(table_ui=self.parent.ui.summary_table)
        o_table.insert_item(row=0, column=0, value=int(bin_index_1), format_str="{:d}")
        o_table.insert_item(row=1, column=0, value=int(bin_index_2), format_str="{:d}")

        list_bin_positions = self.parent.list_bin_positions

        # file index
        (from_file_index, to_file_index) = SelectionTab.get_file_index_range(bin_index=bin_index_1,
                                                                             list_bin_positions=list_bin_positions)
        o_table.insert_item(row=0, column=1, value=from_file_index, format_str="{:d}")
        o_table.insert_item(row=0, column=2, value=to_file_index, format_str="{:d}")

        (from_file_index, to_file_index) = SelectionTab.get_file_index_range(bin_index=bin_index_2,
                                                                             list_bin_positions=list_bin_positions)
        o_table.insert_item(row=1, column=1, value=from_file_index, format_str="{:d}")
        o_table.insert_item(row=1, column=2, value=to_file_index, format_str="{:d}")

        # tof index
        (from_tof_index, to_tof_index) = SelectionTab.get_tof_index_range(bin_index=bin_index_1,
                                                                          list_bin_positions=list_bin_positions)
        o_table.insert_item(row=0, column=3, value=from_tof_index * 1e6, format_str="{:f}")
        o_table.insert_item(row=0, column=4, value=to_tof_index * 1e6, format_str="{:f}")

        (from_tof_index, to_tof_index) = SelectionTab.get_tof_index_range(bin_index=bin_index_2,
                                                                          list_bin_positions=list_bin_positions)
        o_table.insert_item(row=1, column=3, value=from_tof_index * 1e6, format_str="{:f}")
        o_table.insert_item(row=1, column=4, value=to_tof_index * 1e6, format_str="{:2f}")

        # lambda index
        (from_lambda_index, to_lambda_index) = SelectionTab.get_lambda_index_range(bin_index=bin_index_1,
                                                                                   list_bin_positions=list_bin_positions)
        o_table.insert_item(row=0, column=5, value=from_lambda_index, format_str="{:f}")
        o_table.insert_item(row=0, column=6, value=to_lambda_index, format_str="{:f}")

        (from_lambda_index, to_lambda_index) = SelectionTab.get_lambda_index_range(bin_index=bin_index_2,
                                                                                   list_bin_positions=list_bin_positions)
        o_table.insert_item(row=1, column=5, value=from_lambda_index, format_str="{:f}")
        o_table.insert_item(row=1, column=6, value=to_lambda_index, format_str="{:f}")

    def initialize_table(self, nbr_bin=0):
        o_table = TableHandler(table_ui=self.parent.ui.calculation_bin_table)
        o_table.full_reset()

        list_row_col_names = []
        for bin_index in np.arange(nbr_bin):
            o_table.insert_empty_row(row=bin_index)
            o_table.insert_empty_column(column=bin_index)
            list_row_col_names.append("Bin #{}".format(bin_index))

        o_table.set_row_names(row_names=list_row_col_names)
        o_table.set_column_names(column_names=list_row_col_names)

    def display_image_of_best_ratio(self):
        list_bin_positions = self.parent.list_bin_positions
        list_bin_index = list_bin_positions['index']

        optimum_bin_ratio = self.parent.optimum_bin_ratio
        data = self.parent.o_norm.data['sample']['data']

        # image 1
        from_index = optimum_bin_ratio['bin_number_1']
        to_index = from_index + 1
        image_stack1 = data[list_bin_index[from_index]: list_bin_index[to_index]][:][:]
        image1 = np.mean(image_stack1, axis=0)

        # image 2
        from_index = optimum_bin_ratio['bin_number_2']
        to_index = from_index + 1
        image_stack2 = data[list_bin_index[from_index]: list_bin_index[to_index]][:][:]
        image2 = np.mean(image_stack2, axis=0)

        index_of_0 = np.where(image2 == 0)
        image2[index_of_0] = np.NaN
        image1_over_image2 = np.true_divide(image1, image2)

        _image = np.transpose(image1_over_image2)
        self.parent.ui.image_ratio_view.setImage(_image)

        o_table = TableHandler(table_ui=self.parent.ui.calculation_bin_table)
        o_table.select_cell(row=optimum_bin_ratio['bin_number_1'],
                            column=optimum_bin_ratio['bin_number_2'])
        self.save_widget_enabled(enabled=True)
        self.parent.calculated_live_image = _image

    def display_image_of_selected_cell(self, row=0, column=0):
        if row > column:
            self.parent.ui.image_ratio_view.clear()
            self.save_widget_enabled(enabled=False)
            return
        elif row == column:
            self.save_widget_enabled(enabled=False)
        else:
            self.save_widget_enabled(enabled=True)

        data = self.parent.o_norm.data['sample']['data']
        list_bin_positions = self.parent.list_bin_positions
        list_bin_index = list_bin_positions['index']

        from_index1 = row
        to_index1 = from_index1 + 1
        image_stack1 = data[list_bin_index[from_index1]: list_bin_index[to_index1]][:][:]
        image1 = np.mean(image_stack1, axis=0)

        from_index2 = column
        to_index2 = from_index2 + 1
        image_stack2 = data[list_bin_index[from_index2]: list_bin_index[to_index2]][:][:]
        image2 = np.mean(image_stack2, axis=0)

        index_of_0 = np.where(image2 == 0)
        image2[index_of_0] = np.NaN
        image1_over_image2 = np.true_divide(image1, image2)

        _image = np.transpose(image1_over_image2)
        self.parent.ui.image_ratio_view.setImage(_image)
        self.parent.calculated_live_image = _image

    def save_widget_enabled(self, enabled=True):
        self.parent.ui.export_image_button.setEnabled(enabled)

    def make_image_name(self, full_base_folder=""):
        o_table = TableHandler(table_ui=self.parent.ui.calculation_bin_table)
        (row, col) = o_table.get_cell_selected()
        base_folder = os.path.basename(full_base_folder)
        image_name = "{}_bin{}_divided_by_bin{}.tiff".format(base_folder,
                                                             col,
                                                             row)
        return image_name

    def export_selected_image(self):
        base_folder = Path(self.parent.working_dir)
        image_name = self.make_image_name(base_folder)
        export_file_tuple = QFileDialog.getSaveFileName(parent=self.parent,
                                                        directory=str(base_folder) + "/" + image_name,
                                                        caption="Define output image name (*.tiff)")
        if export_file_tuple[0]:
            export_file_name = export_file_tuple[0]
            image_to_save = self.parent.calculated_live_image

            folder_where_to_save = os.path.dirname(export_file_name)
            base_export_file_name = os.path.basename(export_file_name)

            metadata = self.parent.o_norm.data['sample']['metadata'][0]
            o_norm = Normalization()
            o_norm.data['sample']['data'] = [image_to_save]
            o_norm.data['sample']['metadata'] = [metadata]
            o_norm.data['sample']['file_name'] = [base_export_file_name]
            o_norm.export(folder=folder_where_to_save,
                          data_type='sample')
