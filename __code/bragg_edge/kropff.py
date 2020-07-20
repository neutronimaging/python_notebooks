import numpy as np

from __code.table_handler import TableHandler


class Kropff:

	def __init__(self, parent=None):
		self.parent = parent

		self.table_ui = {'high_lambda': self.parent.ui.high_lambda_tableWidget,
		                 'low_lambda' : self.parent.ui.low_lambda_tableWidget,
		                 'bragg_peak' : self.parent.ui.bragg_edge_tableWidget}

	def reset_all_table(self):
		self.reset_high_lambda_table()
		self.reset_low_lambda_table()
		self.reset_bragg_peak_table()

	def reset_high_lambda_table(self):
		self.clear_table(table_name='high_lambda')
		self.fill_table_with_minimum_contain(table_ui=self.parent.ui.high_lambda_tableWidget)

	def reset_low_lambda_table(self):
		self.clear_table(table_name='low_lambda')
		self.fill_table_with_minimum_contain(table_ui=self.parent.ui.low_lambda_tableWidget)

	def reset_bragg_peak_table(self):
		self.clear_table(table_name='bragg_peak')
		self.fill_table_with_minimum_contain(table_ui=self.parent.ui.bragg_edge_tableWidget)

	def clear_table(self, table_name='high_lambda', is_all=False):
		"""remove all the rows of the table name specified, or all if is_all is True"""
		if is_all:
			for _key in self.table_ui.keys():
				self.clear_table(table_name=_key)
		else:
			o_table = TableHandler(table_ui=self.table_ui[table_name])
			o_table.remove_all_rows()

	def fill_table_with_minimum_contain(self, table_ui=None):
		fitting_input_dictionary = self.parent.fitting_input_dictionary
		rois = fitting_input_dictionary['rois']

		o_table = TableHandler(table_ui=table_ui)
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

	def fill_table_with_fitting_information(self):
		fitting_input_dictionary = self.parent.fitting_input_dictionary

		o_table = TableHandler(table_ui=self.table_ui['high_lambda'])
		_col = 1
		for _row in fitting_input_dictionary['rois'].keys():
			_entry = fitting_input_dictionary['rois'][_row]['fitting']['kropff']['high']
			o_table.set_item_with_float(_row, _col, _entry['a0'])
			o_table.set_item_with_float(_row, _col+1, _entry['b0'])
			o_table.set_item_with_float(_row, _col+2, _entry['a0_error'])
			o_table.set_item_with_float(_row, _col+3, _entry['b0_error'])

		o_table = TableHandler(table_ui=self.table_ui['low_lambda'])
		_col = 1
		for _row in fitting_input_dictionary['rois'].keys():
			_entry = fitting_input_dictionary['rois'][_row]['fitting']['kropff']['low']
			o_table.set_item_with_float(_row, _col, _entry['ahkl'])
			o_table.set_item_with_float(_row, _col+1, _entry['bhkl'])
			o_table.set_item_with_float(_row, _col+2, _entry['ahkl_error'])
			o_table.set_item_with_float(_row, _col+3, _entry['bhkl_error'])

		o_table = TableHandler(table_ui=self.table_ui['bragg_peak'])
		_col = 1
		for _row in fitting_input_dictionary['rois'].keys():
			_entry = fitting_input_dictionary['rois'][_row]['fitting']['kropff']['bragg_peak']
			o_table.set_item_with_float(_row, _col, _entry['lambdahkl'])
			o_table.set_item_with_float(_row, _col+1, _entry['tau'])
			o_table.set_item_with_float(_row, _col+2, _entry['sigma'])
			o_table.set_item_with_float(_row, _col+3, _entry['lambdahkl_error'])
			o_table.set_item_with_float(_row, _col+4, _entry['tau_error'])
			o_table.set_item_with_float(_row, _col+5, _entry['sigma_error'])
