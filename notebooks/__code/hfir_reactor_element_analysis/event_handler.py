from qtpy import QtGui
from qtpy.QtWidgets import QMenu
import numpy as np

from __code._utilities.table_handler import TableHandler
from __code._utilities.array import reject_n_outliers, get_closest_index


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def list_of_images_right_click(self):
        menu = QMenu(self.parent)
        unsellect_all = menu.addAction("Unselect all")
        remove_selected_rows = menu.addAction("Remove selected row(s)")
        action = menu.exec_(QtGui.QCursor.pos())

        if action == unsellect_all:
            self.unselect_all()
        elif action == remove_selected_rows:
            self.remove_selected_rows()

    def remove_selected_rows(self):
        selection = self.parent.ui.listWidget.selectedItems()
        list_file_selected = [_item.text() for _item in selection]
        pandas_obj = self.parent.o_selection.pandas_obj
        pandas_obj = pandas_obj.drop(list_file_selected, axis=1)
        self.parent.o_selection.pandas_obj = pandas_obj
        list_of_images = pandas_obj.columns
        self.parent.list_of_images = list_of_images
        self.update_list_of_images_table()

    def update_list_of_images_table(self):
        list_of_images = self.parent.list_of_images
        self.parent.ui.listWidget.clear()
        self.parent.ui.listWidget.addItems(list_of_images)
        self.parent.ui.listWidget.setCurrentRow(0)

    def unselect_all(self):
        self.parent.ui.listWidget.clearSelection()

    def list_of_images_selection_changed(self):
        selection = self.parent.ui.listWidget.selectedItems()
        list_file_selected = [_item.text() for _item in selection]
        pandas_obj = self.parent.o_selection.pandas_obj

        x_axis = np.array(pandas_obj.index)
        list_y_axis = []
        for _file in list_file_selected:
            _y_axis = np.array(pandas_obj[_file])
            list_y_axis.append(_y_axis)

        self.parent.profiles_plot.axes.clear()
        self.parent.profiles_plot.draw()

        plot_type = '-'
        if self.parent.ui.plus_radioButton.isChecked():
            plot_type = '+'
        elif self.parent.ui.point_radioButton.isChecked():
            plot_type = "."

        for _index, _y_axis in enumerate(list_y_axis):
            self.parent.profiles_plot.axes.plot(x_axis, _y_axis, plot_type, label=list_file_selected[_index])
            self.parent.profiles_plot.axes.legend()
            self.parent.profiles_plot.axes.set_title("Profile of selected images")

        if self.parent.global_list_of_xy_max:
            for _file in list_file_selected:
                x_max = self.parent.global_list_of_xy_max[_file]['x']
                y_max = self.parent.global_list_of_xy_max[_file]['y']
                self.parent.profiles_plot.axes.plot(x_max, y_max, '*r')

        # thresholds
        threshold = self.parent.ui.threshold_slider.value()
        self.parent.profiles_plot.axes.axhline(threshold, linestyle='--', color='red')
        self.parent.profiles_plot.draw()

    def get_profile_of_file_index(self, file_index):
        pandas_obj = self.parent.o_pandas
        file_index_name = self.parent.o_pandas.columns[file_index]
        profile_of_file = pandas_obj[file_index_name]
        return profile_of_file

    def get_profile_of_selected_files(self):
        list_file_index_selected = self.parent.get_list_file_index_selected()
        list_profiles = []
        for _file_index in list_file_index_selected:
            _profile = self.get_profile_of_file_index(_file_index)
            list_profiles.append(_profile)
        return list_profiles

    def threshold_clicked(self):
        self.parent.list_of_images_selection_changed()

    def threshold_moved(self, value):
        self.parent.list_of_images_selection_changed()

    def calculate_elements_position(self):
        list_of_images = self.parent.list_of_images
        global_list_of_xy_max = {}

        self.parent.eventProgress.setMaximum(len(list_of_images))
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)

        pandas_obj = self.parent.o_selection.pandas_obj
        self.working_x_axis = np.array(pandas_obj.index)

        for _file_index, _file in enumerate(list_of_images):
            working_y_axis = np.array(pandas_obj[_file])
            _dict = self.calculate_list_of_local_max(working_y_axis=working_y_axis)
            _dict = {'x': _dict['x'],
                     'y': _dict['y']}
            global_list_of_xy_max[_file] = _dict

            self.parent.eventProgress.setValue(_file_index+1)
            QtGui.QGuiApplication.processEvents()

        self.parent.global_list_of_xy_max = global_list_of_xy_max
        self.parent.eventProgress.setVisible(False)

    def calculate_list_of_local_max(self, working_y_axis=None):

        working_x_axis = self.working_x_axis
        threshold = self.parent.ui.threshold_slider.value()

        list_of_x_of_local_max = []
        list_of_y_max = []
        local_y_max = 0
        x_of_local_max = 0
        minimum_number_of_points_to_high_region = self.parent.ui.minimum_number_of_points_spinBox.value()
        number_of_points_in_current_high_region = 0
        for _x_value, _y_value in zip(working_x_axis, working_y_axis):

            if _y_value < threshold:

                if local_y_max != 0:
                    if number_of_points_in_current_high_region >= minimum_number_of_points_to_high_region:
                        list_of_x_of_local_max.append(x_of_local_max)
                        list_of_y_max.append(local_y_max)
                        local_y_max = 0

                number_of_points_in_current_high_region = 0
                continue

            else:

                if _y_value > local_y_max:
                    x_of_local_max = _x_value
                    local_y_max = _y_value

                number_of_points_in_current_high_region += 1

        return {'x': list_of_x_of_local_max,
                'y': list_of_y_max}

    def populate_elements_position_tab(self):
        self.populate_elements_position_plot()
        self.populate_elements_position_table()
        self.populate_error_tables()
        self.plot_average_position()

    def populate_elements_position_plot(self):
        global_list_of_xy_max = self.parent.global_list_of_xy_max
        list_of_images = self.parent.list_of_images

        self.parent.elements_position.axes.clear()
        self.parent.elements_position.draw()

        plot_type = "."

        for _file_index, _file in enumerate(list_of_images):
            x_axis = global_list_of_xy_max[_file]['x']
            y_axis = np.ones((len(x_axis)))*(_file_index+1)
            self.parent.elements_position.axes.plot(x_axis, y_axis, plot_type)

        self.parent.elements_position.axes.invert_yaxis()
        self.parent.elements_position.draw()

    def plot_average_position(self):
        list_mean_position_of_elements = self.get_list_mean_position_of_elements()
        ymin = 0
        ymax = len(self.parent.list_of_images)
        for _value in list_mean_position_of_elements:
            self.parent.elements_position.axes.vlines(_value, ymin, ymax, colors=(1, 0, 0, 1))

    def populate_elements_position_table(self):
        global_list_of_xy_max = self.parent.global_list_of_xy_max
        # global_list_of_xy_mean = self.parent.global_list_of_xy_mean
        list_of_images = self.parent.list_of_images

        o_table = TableHandler(table_ui=self.parent.elements_position_tableWidget)
        o_table.remove_all_rows()
        raw_table = []
        nbr_column = 0
        for _row, _file in enumerate(list_of_images):
            o_table.insert_empty_row(_row)
            x_axis = global_list_of_xy_max[_file]['x']
            raw_table.append(x_axis)
            if len(x_axis) > nbr_column: nbr_column = len(x_axis)
            for _column in np.arange(len(x_axis)):
                if _row == 0:
                    o_table.insert_column(_column)
                o_table.insert_item(row=_row, column=_column, value="", editable=False)

        nbr_row = len(list_of_images)

        col_width = np.ones((nbr_column)) * 5
        row_height = np.ones((nbr_row)) * 5
        o_table.set_column_width(column_width=col_width)
        o_table.set_row_height(row_height=row_height)

        self.parent.elements_position_raw_table = raw_table
        self.parent.elements_position_formatted_raw_table = self.format_table(raw_table)

    def populate_error_tables(self):
        self.display_background_error_in_elements_position_table()
        self.display_missing_peaks_table()

    def display_background_error_in_elements_position_table(self):
        median_number_of_elements = self.get_median_number_of_elements()
        nbr_row = len(self.parent.list_of_images)
        nbr_column = np.int(median_number_of_elements)

        ideal_table_data_error = np.zeros((nbr_row, nbr_column))
        error_table = list()

        list_mean_position_of_elements = self.get_list_mean_position_of_elements()
        self.parent.list_ideal_position_of_elements = list_mean_position_of_elements
        tolerance = self.parent.ui.tolerance_value_doubleSpinBox.value()

        mean_angle_offset_between_elements = self.get_mean_angle_offset_between_elements()
        list_average = np.arange(list_mean_position_of_elements[0],
                                 nbr_column*mean_angle_offset_between_elements,
                                 mean_angle_offset_between_elements)

        data = self.parent.elements_position_formatted_raw_table

        data_filename = '/Users/j35/Desktop/data_file'
        np.save(data_filename, data, allow_pickle=True)

        for _row_index, _row in enumerate(data):
            _reference_index_element = 0
            _error_row = []

            for _index_element, _element_position in enumerate(_row):
                found_flag = True

                if _reference_index_element == len(list_average):
                    # we are done for this row
                    _error_row.append(0)
                    break

                while ((_element_position < (list_average[_reference_index_element] - tolerance)) or
                       (_element_position > (list_average[_reference_index_element] + tolerance))):

                    if _element_position < list_average[_reference_index_element]:
                        _error_row.append(0)
                        found_flag = False
                        break

                    _reference_index_element += 1
                    if _reference_index_element > len(list_average) - 1:
                        _error_row.append(0)
                        found_flag = False
                        break

                if found_flag:
                    # find the closest place where this _element_position goes
                    nearest_index = get_closest_index(array=list_average,
                                                      value=_element_position)
                    ideal_table_data_error[_row_index, nearest_index] = 1

                    _reference_index_element += 1
                    _error_row.append(1)
                if not found_flag:
                    pass

            error_table.append(_error_row)

        self.parent.ideal_table_data_error = ideal_table_data_error

        o_table = TableHandler(table_ui=self.parent.elements_position_tableWidget)
        (nbr_row, nbr_column) = np.shape(data)
        for _row in np.arange(nbr_row):
            for _column, _state in enumerate(error_table[_row]):
                if _state == 0:
                    if o_table.is_item(row=_row, column=_column):
                        o_table.set_background_color(row=_row,
                                                     column=_column,
                                                     qcolor=QtGui.QColor(150, 0, 0))

    def display_missing_peaks_table(self):
        ideal_table_data_error = self.parent.ideal_table_data_error
        o_table = TableHandler(table_ui=self.parent.missing_peaks_tableWidget)
        o_table.full_reset()
        (nbr_row, nbr_column) = np.shape(ideal_table_data_error)
        for _row in np.arange(nbr_row):
            o_table.insert_empty_row(row=_row)
            for _column in np.arange(nbr_column):
                if _row == 0:
                    o_table.insert_empty_column(_column)
                o_table.insert_item(row=_row, column=_column, value="", editable=False)
                value = ideal_table_data_error[_row, _column]
                if value == 1:
                    # green
                    color = QtGui.QColor(0, 255, 0)
                else:
                    color = QtGui.QColor(255, 0, 0)
                o_table.set_background_color(row=_row,
                                             column=_column,
                                             qcolor=color)

        col_width = np.ones((nbr_column)) * 5
        row_height = np.ones((nbr_row)) * 5
        o_table.set_column_width(column_width=col_width)
        o_table.set_row_height(row_height=row_height)

    def populate_error_table_backup(self):
        median_number_of_elements = self.get_median_number_of_elements()

        nbr_row = len(self.parent.list_of_images)
        nbr_column = np.int(median_number_of_elements)
        elements_position_error_table = np.zeros((nbr_row, nbr_column))
        # mean_angle_offset_between_elements = self.get_mean_angle_offset_between_elements()
        self.parent.list_mean_position_of_elements = self.get_list_mean_position_of_elements()
        self.tolerance_value = self.parent.ui.tolerance_value_doubleSpinBox.value()

        for _row_index in np.arange(nbr_row):
            for _col_index, _col_value in enumerate(self.parent.elements_position_formatted_raw_table[_row_index]):
                col_index = self.where_value_found_within_expected_tolerance(value=_col_value)
                if col_index >= 0:
                    elements_position_error_table[_row_index, col_index] += 1  # we found an element at that position
                    # if a value > 1 is found later on when checking the table, an error will be displayed for that
                    # cell
                elif col_index == -1:
                    closer_col_index = get_closest_index(value=_col_value,
                                                         array=self.parent.list_mean_position_of_elements)
                    elements_position_error_table[_row_index, closer_col_index] = -10  # very low value to make sure
                    # an error will show up in this cell

        o_table = TableHandler(table_ui=self.parent.error_tableWidget)
        o_table.full_reset()

        for _row_index in np.arange(nbr_row):
            for _col_index in np.arange(nbr_column):
                if _row_index == 0:
                    o_table.insert_empty_column(_col_index)
                o_table.insert_empty_row(_row_index)
                _value = elements_position_error_table[_row_index, _col_index]
                o_table.insert_item_with_float(row=_row_index,
                                               column=_col_index,
                                               float_value=_value)

    def is_value_within_expected_tolerance(self, value_to_check=None,
                                           value_expected=None):
        tolerance_value = self.tolerance_value
        if (value_to_check >= (value_expected - tolerance_value)) and \
            (value_to_check <= (value_expected + tolerance_value)):
            return True
        return False

    def where_value_found_within_expected_tolerance(self, value=np.NaN):
        """
        will return the index where the value was found within the expected tolerance. If
        none can be found, it will return -1
        """
        tolerance_value = self.tolerance_value
        list_of_ideal_elements_position = self.parent.list_mean_position_of_elements

        for _index, ideal_position in enumerate(list_of_ideal_elements_position):
            if (value >= (ideal_position - tolerance_value)) and \
               (value <= (ideal_position + tolerance_value)):
                return _index

        return -1

    def get_mean_angle_offset_between_elements(self):
        list_mean_position = self.get_list_mean_position_of_elements()
        return list_mean_position[1] - list_mean_position[0]

        # table = self.parent.elements_position_formatted_raw_table
        # [nbr_row, nbr_column] = np.shape(table)
        #
        # number_of_outliers_to_reject = np.int((self.parent.percent_of_outliers_to_reject / 100) * nbr_row)
        # list_mean_value = []
        # for _column_index in np.arange(nbr_column):
        #     _col_value = table[:, _column_index]
        #     _col_value_without_outliers = reject_n_outliers(array=_col_value, n=number_of_outliers_to_reject)
        #     list_mean_value.append(np.nanmean(_col_value))
        #
        # self.parent.list_mean_position_of_elements = list_mean_value
        #
        # left_array = np.array(list_mean_value[:-1])
        # right_array = np.array(list_mean_value[1:])
        # delta_value = right_array - left_array
        #
        # return np.mean(delta_value)

    def get_list_mean_position_of_elements(self):
        table = self.parent.elements_position_formatted_raw_table
        [nbr_row, nbr_column] = np.shape(table)

        number_of_outliers_to_reject = np.int((self.parent.percent_of_outliers_to_reject / 100) * nbr_row)
        # list_mean_value = []
        # for _column_index in np.arange(nbr_column):
        #     _col_value = table[:, _column_index]
        #     _col_value_without_outliers = reject_n_outliers(array=_col_value, n=number_of_outliers_to_reject)
        #     list_mean_value.append(np.nanmean(_col_value))

        # mean of first element
        _col_value = table[:, 0]
        _col_value_without_outliers = reject_n_outliers(array=_col_value,
                                                        n=number_of_outliers_to_reject)
        mean_first_element = np.nanmean(_col_value)

        # trying to calculate manually ideal list mean
        nbr_elements = self.parent.ui.number_of_elements_spinBox.value()
        angle_step = np.float(360) / np.float(nbr_elements)
        list_mean_value = np.arange(mean_first_element, 360, angle_step)

        return list_mean_value

    def get_median_number_of_elements(self):
        table = self.parent.elements_position_raw_table
        list_number_of_elements = []
        for _row in table:
            nbr_elements = len(_row)
            list_number_of_elements.append(nbr_elements)

        return np.median(list_number_of_elements)

    def format_table(self, raw_table=None):
        max_number_of_elements = np.max([len(list_of_elements) for list_of_elements in raw_table])
        number_of_rows = len(raw_table)
        formatted_table = np.empty((number_of_rows, max_number_of_elements))
        formatted_table[:] = np.NaN

        for _row, _list in enumerate(raw_table):
            for _column, _value in enumerate(_list):
                formatted_table[_row, _column] = _value
        return formatted_table
