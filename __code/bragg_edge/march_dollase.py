from qtpy import QtGui
import numpy as np
import pyqtgraph as pg
from qtpy.QtWidgets import QFileDialog
from pathlib import Path

from __code.table_handler import TableHandler
from __code.bragg_edge.bragg_edge_peak_fitting_gui_utility import GuiUtility
from __code.bragg_edge.get import Get
from __code.utilities import find_nearest_index


class MarchDollase:

	list_columns = ['d_spacing', 'sigma', 'alpha', 'a1', 'a2', 'a5', 'a6',
	                'd_spacing_error', 'sigma_error', 'alpha_error',
	                'a1_error', 'a2_error', 'a5_error', 'a6_error']

	def __init__(self, parent=None):
		self.parent = parent
		self.history_table_ui = self.parent.ui.march_dollase_user_input_table
		self.result_table_ui = self.parent.ui.march_dollase_result_table

	def reset_table(self):
		self.reset_result_table()
		self.reset_history_table()

	def reset_result_table(self):
		"""remove all the rows of the table name specified, or all if is_all is True"""
		o_table = TableHandler(table_ui=self.result_table_ui)
		o_table.remove_all_rows()
		self.fill_table_with_minimum_contain()

	def reset_history_table(self):
		o_table = TableHandler(table_ui=self.history_table_ui)
		o_table.remove_all_rows()

	def fill_table_with_minimum_contain(self):
		fitting_input_dictionary = self.parent.fitting_input_dictionary
		rois = fitting_input_dictionary['rois']

		o_table = TableHandler(table_ui=self.result_table_ui)
		nbr_column = o_table.table_ui.columnCount()
		other_column_name = ["N/A" for _ in np.arange(nbr_column)]
		for _row, _roi in enumerate(rois.keys()):
			_roi_key = rois[_roi]
			list_col_name = "{}; {}; {}; {}".format(_roi_key['x0'],
			                                        _roi_key['y0'],
			                                        _roi_key['width'],
			                                        _roi_key['height'])
			col_name = [list_col_name] + other_column_name
			o_table.insert_row(_row, col_name)

	def table_clicked(self, row=None, column=None):
		nbr_row = self.history_table_ui.rowCount()

		enabled_up_button = True
		enabled_down_button = True

		if row == 0:
			enabled_up_button = False
		if row == (nbr_row - 1):
			enabled_down_button = False

		self.parent.ui.march_dollase_user_input_up.setEnabled(enabled_up_button)
		self.parent.ui.march_dollase_user_input_down.setEnabled(enabled_down_button)
		self.parent.ui.march_dollase_user_input_table.setFocus()

	def get_row_selected(self):
		o_table = TableHandler(table_ui=self.parent.march_dollase_user_input_table)
		row_selected = o_table.get_row_selected()
		return row_selected

	def move_row_up(self):
		self.move_table_row(to_row_offset=-1)

	def move_row_down(self):
		self.move_table_row(to_row_offset=+1)

	def move_table_row(self, to_row_offset=-1):
		"""
		:param to_row_offset: +1 means moving row to the next row, -1 means moving up by one row
		"""
		row_selected = self.get_row_selected()
		march_dollase_fitting_history_table = self.parent.march_dollase_fitting_history_table
		row_to_move = march_dollase_fitting_history_table.pop(row_selected)

		new_row = row_selected + to_row_offset

		march_dollase_fitting_history_table.insert(new_row, row_to_move)
		self.parent.march_dollase_fitting_history_table = march_dollase_fitting_history_table

		o_gui = GuiUtility(parent=self.parent)
		o_gui.fill_march_dollase_table(list_state=self.parent.march_dollase_fitting_history_table,
		                               list_initial_parameters=self.parent.march_dollase_fitting_initial_parameters)

		# keep current selection on new row
		o_table = TableHandler(table_ui=self.parent.march_dollase_user_input_table)
		o_table.select_row(row=new_row)
		self.table_clicked(row=new_row)

	def table_right_clicked(self):
		table_is_empty = False
		list_state = self.parent.march_dollase_fitting_history_table

		if not list_state:
			table_is_empty = True

		menu = QtGui.QMenu(self.parent)

		insert_row = -1

		insert_above = -1
		insert_below = -1
		duplicate_row = -1
		delete_row = -1

		if table_is_empty:
			insert_row = menu.addAction("Insert Row")

		else:
			insert_above = menu.addAction("Insert Row Above")
			insert_below = menu.addAction("Insert Row Below")
			menu.addSeparator()
			duplicate_row = menu.addAction("Duplicate Row")
			menu.addSeparator()
			delete_row = menu.addAction("Remove Row")
			menu.addSeparator()
			full_reset = menu.addAction("Full Table Reset")

		action = menu.exec_(QtGui.QCursor.pos())

		if action == insert_above:
			self.insert_row_above()
		elif action == insert_below:
			self.insert_row_below()
		elif action == duplicate_row:
			self.duplicate_row()
		elif action == delete_row:
			self.delete_row()
		elif action == insert_row:
			self.insert_row()
		elif action == full_reset:
			self.full_reset()
		else:
			pass

	def insert_row(self):
		march_dollase_fitting_history_table = list()
		new_entry = self.parent.march_dollase_fitting_history_table_default_new_row
		march_dollase_fitting_history_table.insert(0, new_entry)
		self.parent.march_dollase_fitting_history_table = march_dollase_fitting_history_table
		self.update_table_after_changing_row(changing_row=0)

	def insert_row_above(self):
		o_table = TableHandler(table_ui=self.parent.ui.march_dollase_user_input_table)
		row_selected = o_table.get_row_selected()
		march_dollase_fitting_history_table = self.parent.march_dollase_fitting_history_table
		new_entry = [False for _entry in march_dollase_fitting_history_table[0]]
		march_dollase_fitting_history_table.insert(row_selected, new_entry)
		self.parent.march_dollase_fitting_history_table = march_dollase_fitting_history_table
		self.update_table_after_changing_row(changing_row=row_selected+1)

	def insert_row_below(self):
		o_table = TableHandler(table_ui=self.parent.ui.march_dollase_user_input_table)
		row_selected = o_table.get_row_selected()
		march_dollase_fitting_history_table = self.parent.march_dollase_fitting_history_table
		new_entry = [False for _entry in march_dollase_fitting_history_table[0]]
		march_dollase_fitting_history_table.insert(row_selected+1, new_entry)
		self.parent.march_dollase_fitting_history_table = march_dollase_fitting_history_table
		self.update_table_after_changing_row(changing_row=row_selected+2)

	def duplicate_row(self):
		o_table = TableHandler(table_ui=self.parent.ui.march_dollase_user_input_table)
		row_selected = o_table.get_row_selected()
		march_dollase_fitting_history_table = self.parent.march_dollase_fitting_history_table
		new_entry = march_dollase_fitting_history_table[row_selected]
		march_dollase_fitting_history_table.insert(row_selected, new_entry)
		self.parent.march_dollase_fitting_history_table = march_dollase_fitting_history_table
		self.update_table_after_changing_row(changing_row=row_selected+1)

	def delete_row(self):
		o_table = TableHandler(table_ui=self.parent.ui.march_dollase_user_input_table)
		row_selected = o_table.get_row_selected()
		march_dollase_fitting_history_table = self.parent.march_dollase_fitting_history_table
		march_dollase_fitting_history_table.pop(row_selected)
		self.parent.march_dollase_fitting_history_table = march_dollase_fitting_history_table
		self.update_table_after_changing_row(changing_row=row_selected)

	def full_reset(self):
		march_dollase_history_state = self.parent.march_dollase_history_state_full_reset
		o_gui = GuiUtility(parent=self.parent)
		o_gui.fill_march_dollase_table(list_state=march_dollase_history_state,
		                               initial_parameters=self.parent.march_dollase_fitting_initial_parameters)

	def update_table_after_changing_row(self, changing_row=-1):
		o_gui = GuiUtility(parent=self.parent)
		o_gui.fill_march_dollase_table(list_state=self.parent.march_dollase_fitting_history_table,
		                               initial_parameters=self.parent.march_dollase_fitting_initial_parameters)

		# keep current selection on new row
		o_table = TableHandler(table_ui=self.parent.march_dollase_user_input_table)
		o_table.select_row(row=changing_row-1)
		self.table_clicked(row=changing_row)

	def advanced_mode_clicked(self):
		hide_advanced = not self.parent.ui.march_dollase_advanced_mode_checkBox.isChecked()
		o_gui = GuiUtility(parent=self.parent)
		o_gui.set_columns_hidden(table_ui=self.parent.ui.march_dollase_user_input_table,
				                 list_of_columns=[5, 6],
		                         state=hide_advanced)
		o_gui.set_columns_hidden(table_ui=self.parent.ui.march_dollase_result_table,
		                         list_of_columns=[6, 7, 13, 14],
		                         state=hide_advanced)

	def update_fitting_plot(self):
		self.parent.ui.fitting.clear()
		if self.parent.fitting_peak_ui:
			self.parent.ui.fitting.removeItem(self.parent.fitting_peak_ui)

		o_get = Get(parent=self.parent)
		xaxis_checked = o_get.x_axis_checked()
		xaxis = o_get.x_axis_data(x_axis_selected=xaxis_checked)
		xaxis_label = o_get.x_axis_label(x_axis_selected=xaxis_checked)

		o_table = TableHandler(table_ui=self.parent.ui.march_dollase_result_table)
		list_row_selected = o_table.get_rows_of_table_selected()

		if list_row_selected is None:
			return

		for row_selected in list_row_selected:
			yaxis = o_get.y_axis_data_of_selected_row(row_selected=row_selected)
			self.parent.ui.fitting.plot(xaxis, yaxis,
			                            pen=(self.parent.selection_roi_rgb[0],
			                                 self.parent.selection_roi_rgb[1],
			                                 self.parent.selection_roi_rgb[2]),
			                            symbol='o')
			self.parent.ui.fitting.setLabel("bottom", xaxis_label)
			self.parent.ui.fitting.setLabel("left", "Average transmission")

		if self.parent.ui.march_dollase_toolBox.currentIndex() == 0:
			move_bragg_peak_range = True
		else:
			move_bragg_peak_range = False

		peak_range = self.parent.march_dollase_fitting_range_selected
		local_peak_range = [xaxis[peak_range[0]], xaxis[peak_range[1]]]

		if self.parent.march_dollase_fitting_peak_ui:
			self.parent.ui.fitting.removeItem(self.parent.march_dollase_fitting_peak_ui)
		self.parent.march_dollase_fitting_peak_ui = pg.LinearRegionItem(values=local_peak_range,
		                                                                orientation=None,
		                                                                brush=None,
		                                                                movable=move_bragg_peak_range,
		                                                                bounds=None)
		self.parent.march_dollase_fitting_peak_ui.sigRegionChanged.connect(
				self.parent.march_dollase_fitting_range_changed)
		self.parent.march_dollase_fitting_peak_ui.setZValue(-10)
		self.parent.ui.fitting.addItem(self.parent.march_dollase_fitting_peak_ui)
		# self.parent.march_dollase_fitting_range_changed()

	def save_table_history_and_initial_parameters(self):
		march_dollase_fitting_history_table = list()
		march_dollase_fitting_initial_parameters = self.parent.march_dollase_fitting_initial_parameters
		nbr_row = self.history_table_ui.rowCount()
		nbr_column = self.history_table_ui.columnCount()
		for _row in np.arange(nbr_row):
			_row_history = []
			for _col in np.arange(nbr_column):
				_list_widget = self.history_table_ui.cellWidget(_row, _col).children()

				_check_box = _list_widget[1].children()[1]
				_flag = False
				if _check_box.isChecked():
					_flag = True
				_row_history.append(_flag)

				if _row == 0:
					if (_col == 1) or (_col == 2):
						name = self.parent.march_dollase_list_columns[_col]
						_text = _list_widget[-1].text()
						march_dollase_fitting_initial_parameters[name] = _text

			march_dollase_fitting_history_table.append(_row_history)

		self.parent.march_dollase_fitting_history_table = march_dollase_fitting_history_table
		self.parent.march_dollase_fitting_initial_parameters = march_dollase_fitting_initial_parameters

	def fill_tables_with_fitting_information(self):
		self.fill_history_table_with_fitting_information()
		self.fill_result_table_with_fitting_information()

	def fill_result_table_with_fitting_information(self):
		fitting_input_dictionary = self.parent.fitting_input_dictionary
		march_data = fitting_input_dictionary['rois']

		list_columns = self.parent.march_dollase_list_columns
		for _row in march_data.keys():
			_march_entry = march_data[_row]['fitting']['march_dollase']

			for _col, _col_name in enumerate(list_columns):
				_arg_value = _march_entry.get(_col_name)
				self.result_table_ui.item(_row, _col+1).setText(_arg_value)

	def fill_history_table_with_fitting_information(self):
		o_gui = GuiUtility(parent=self.parent)
		o_gui.fill_march_dollase_table(list_state=self.parent.march_dollase_fitting_history_table,
		                               initial_parameters=self.parent.march_dollase_fitting_initial_parameters)

	def get_initial_parameter_value(self, column=-1):
		name = self.parent.march_dollase_list_columns[column]
		return str(self.parent.march_dollase_fitting_initial_parameters[name])

	def update_roi_labels(self):
		[global_left_range, global_right_range] = self.parent.bragg_edge_range
		[left_range, right_range] = list(self.parent.march_dollase_fitting_peak_ui.getRegion())

		o_get = Get(parent=self.parent)
		x_axis_selected = o_get.x_axis_checked()
		xaxis_dict = self.parent.fitting_input_dictionary['xaxis']
		xaxis_index, _ = xaxis_dict[x_axis_selected]
		[left_xaxis_index, right_xaxis_index] = [global_left_range, global_right_range]

		xaxis = xaxis_index[left_xaxis_index: right_xaxis_index]

		left_index = find_nearest_index(array=xaxis, value=left_range)
		right_index = find_nearest_index(array=xaxis, value=right_range)

		self.parent.march_dollase_fitting_range_selected = [left_index, right_index]

		xaxis_in_selected_axis = self.parent.fitting_input_dictionary['xaxis'][x_axis_selected][0][
		                         global_left_range: global_right_range]
		real_left_value = xaxis_in_selected_axis[left_index]
		real_right_value = xaxis_in_selected_axis[right_index]
		if x_axis_selected == 'lambda':
			str_format = "{:02f}"
		elif x_axis_selected == 'tof':
			str_format = "{:04.2f}"
		else:
			str_format = "{}"
		real_left_value = str_format.format(real_left_value)
		real_right_value = str_format.format(real_right_value)

		units = Get.units(name=x_axis_selected)
		self.parent.ui.march_dollase_bragg_peak_range_from_value.setText(str(real_left_value))
		self.parent.ui.march_dollase_bragg_peak_range_to_value.setText(str(real_right_value))
		self.parent.ui.march_dollase_from_bragg_peak_range_units.setText(units)
		self.parent.ui.march_dollase_to_bragg_peak_range_units.setText(units)

	def result_table_right_click(self):
		menu = QtGui.QMenu(self.parent)
		export_data = menu.addAction("Export Data ...")
		action = menu.exec_(QtGui.QCursor.pos())

		if action == export_data:
			self.export_data_of_selected_rows()

	def export_data_of_selected_rows(self):
		o_table = TableHandler(table_ui=self.parent.ui.march_dollase_result_table)
		list_of_rows_selected = o_table.get_rows_of_table_selected()
		fitting_input_dictionary = self.parent.fitting_input_dictionary

		o_get = Get(parent=self.parent)
		xaxis_index = o_get.x_axis_data(x_axis_selected='index')
		xaxis_tof = o_get.x_axis_data(x_axis_selected='tof')
		xaxis_lambda = o_get.x_axis_data(x_axis_selected='lambda')

		xaxis_index_label = o_get.x_axis_label(x_axis_selected='index')
		xaxis_tof_label = o_get.x_axis_label(x_axis_selected='tof')
		xaxis_lambda_label = o_get.x_axis_label(x_axis_selected='lambda')

		# metadata

		metadata = ["#Marche Dollase Result of Fitting"]
		is_advance_mode = self.parent.ui.march_dollase_advanced_mode_checkBox.isChecked()
		metadata.append("#Using advanced fitting mode: {}".format(is_advance_mode))

		data_label = "#image index, TOF(micros), Lambda(Angstroms)"
		data = []
		for _row in list_of_rows_selected:
			_entry = fitting_input_dictionary['rois'][_row]['fitting']['march_dollase']
			_line = "#-> row {}: d_spacing:{}, sigma:{}, alpha:{}, a1:{}, a2:{}".format(_row,
			                                                                            _entry['d_spacing'],
			                                                                            _entry['sigma'],
			                                                                            _entry['alpha'],
			                                                                            _entry['a1'],
			                                                                            _entry['a2'])
			if is_advance_mode:
				_line += ", a5:{}, a6:{}".format(_entry['a5'], _entry['a6'])
			metadata.append(_line)
			data_label += ", row {}".format(_row)

			data.append(o_get.y_axis_data_of_selected_row(row_selected=_row))

		metadata.append("#")
		metadata.append(data_label)

		print(metadata)

		base_folder = Path(self.parent.working_dir)
		directory = str(base_folder.parent)
		_export_folder = QFileDialog.getExistingDirectory(self.parent,
		                                                  directory=directory,
		                                                  caption="Select Output Folder")

		if _export_folder:
			print(f"folder is: {_export_folder}")






