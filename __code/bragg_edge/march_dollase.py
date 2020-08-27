from qtpy import QtGui
import numpy as np

from __code.table_handler import TableHandler
from __code.bragg_edge.bragg_edge_peak_fitting_gui_utility import GuiUtility
from __code.bragg_edge.get import Get


class MarchDollase:

	def __init__(self, parent=None):
		self.parent = parent
		self.table_ui = self.parent.ui.march_dollase_user_input_table
		self.result_table_ui = self.parent.ui.march_dollase_result_table

	def reset_table(self):
		self.reset_result_table()

	def reset_result_table(self):
		"""remove all the rows of the table name specified, or all if is_all is True"""
		o_table = TableHandler(table_ui=self.result_table_ui)
		o_table.remove_all_rows()
		self.fill_table_with_minimum_contain()

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
		nbr_row = self.table_ui.rowCount()

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

	def update_table_after_changing_row(self, changing_row=-1):
		o_gui = GuiUtility(parent=self.parent)
		o_gui.fill_march_dollase_table(list_state=self.parent.march_dollase_fitting_history_table,
		                               list_initial_parameters=self.parent.march_dollase_fitting_initial_parameters)

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
		x_axis_selected = o_get.x_axis_checked()

		xaxis_dict = self.parent.fitting_input_dictionary['xaxis']
		xaxis_index, xaxis_label = xaxis_dict[x_axis_selected]
		[left_xaxis_index, right_xaxis_index] = self.parent.bragg_edge_range
		xaxis = xaxis_index[left_xaxis_index: right_xaxis_index]

		o_table = TableHandler(table_ui=self.parent.ui.march_dollase_result_table)
		list_row_selected = o_table.get_rows_of_table_selected()

		print(f"list_row_selected: {list_row_selected}")

		selected_roi = self.parent.fitting_input_dictionary['rois'][0]
		yaxis = selected_roi['profile']
		yaxis = yaxis[left_xaxis_index: right_xaxis_index]
		self.parent.ui.fitting.plot(xaxis, yaxis,
		                            pen=(self.parent.selection_roi_rgb[0],
		                                 self.parent.selection_roi_rgb[1],
		                                 self.parent.selection_roi_rgb[2]),
		                            symbol='o')



