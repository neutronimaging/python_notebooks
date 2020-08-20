import numpy as np
from qtpy import QtGui
from qtpy.QtWidgets import QFileDialog
from pathlib import Path

from __code.table_handler import TableHandler
from __code.bragg_edge.bragg_edge_peak_fitting_gui_utility import GuiUtility
from __code.bragg_edge.fitting_job_handler import FittingJobHandler
from __code.file_handler import make_ascii_file_from_2dim_array


class Kropff:

	def __init__(self, parent=None):
		self.parent = parent

		self.table_ui = {'high_tof': self.parent.ui.high_tof_tableWidget,
		                 'low_tof' : self.parent.ui.low_tof_tableWidget,
		                 'bragg_peak' : self.parent.ui.bragg_edge_tableWidget}

	def reset_all_table(self):
		self.reset_high_lambda_table()
		self.reset_low_lambda_table()
		self.reset_bragg_peak_table()

	def reset_high_lambda_table(self):
		self.clear_table(table_name='high_tof')
		self.fill_table_with_minimum_contain(table_ui=self.table_ui['high_tof'])

	def reset_low_lambda_table(self):
		self.clear_table(table_name='low_tof')
		self.fill_table_with_minimum_contain(table_ui=self.table_ui['low_tof'])

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

		o_table = TableHandler(table_ui=self.table_ui['high_tof'])
		_col = 1
		for _row in fitting_input_dictionary['rois'].keys():
			_entry = fitting_input_dictionary['rois'][_row]['fitting']['kropff']['high']
			o_table.set_item_with_float(_row, _col, _entry['a0'])
			o_table.set_item_with_float(_row, _col+1, _entry['b0'])
			o_table.set_item_with_float(_row, _col+2, _entry['a0_error'])
			o_table.set_item_with_float(_row, _col+3, _entry['b0_error'])

		o_table = TableHandler(table_ui=self.table_ui['low_tof'])
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
			o_table.set_item_with_float(_row, _col, _entry['tofhkl'])
			o_table.set_item_with_float(_row, _col+1, _entry['tau'])
			o_table.set_item_with_float(_row, _col+2, _entry['sigma'])
			o_table.set_item_with_float(_row, _col+3, _entry['tofhkl_error'])
			o_table.set_item_with_float(_row, _col+4, _entry['tau_error'])
			o_table.set_item_with_float(_row, _col+5, _entry['sigma_error'])

	def bragg_peak_right_click(self, position=None):
		menu = QtGui.QMenu(self.parent)

		_export = menu.addAction("Export profile of selected row ...")
		action = menu.exec_(QtGui.QCursor.pos())

		if action == _export:
			self.export_bragg_peak_profile()

	def export_bragg_peak_profile(self):
		working_dir = str(Path(self.parent.working_dir).parent)
		_export_folder = QFileDialog.getExistingDirectory(self.parent,
		                                                  directory=working_dir,
		                                                  caption="Select Output Folder")
		# QtGui.QGuiApplication.processEvents()
		if _export_folder:

			o_gui = GuiUtility(parent=self.parent)
			row_selected = o_gui.get_row_of_table_selected(table_ui=self.parent.ui.bragg_edge_tableWidget)

			# make up output file name
			name_of_row = o_gui.get_table_str_item(table_ui=self.parent.ui.bragg_edge_tableWidget,
			                                       row=row_selected,
			                                       column=0)
			[x0, y0, width, height] = name_of_row.split("; ")
			name_of_row_formatted = "x0{}_y0{}_width{}_height{}".format(x0,y0, width, height)
			file_name = "kropff_bragg_peak_profile_{}.txt".format(name_of_row_formatted)
			full_file_name = str(Path(_export_folder) / Path(file_name))

			o_fit = FittingJobHandler(parent=self.parent)
			o_fit.prepare(kropff_tooldbox='bragg_peak')

			x_axis = o_fit.xaxis_to_fit
			y_axis = o_fit.list_yaxis_to_fit[row_selected]

			a0 = self.parent.fitting_input_dictionary['rois'][row_selected]['fitting']['kropff']['high']['a0']
			b0 = self.parent.fitting_input_dictionary['rois'][row_selected]['fitting']['kropff']['high']['b0']
			ahkl = self.parent.fitting_input_dictionary['rois'][row_selected]['fitting']['kropff']['low']['ahkl']
			bhkl = self.parent.fitting_input_dictionary['rois'][row_selected]['fitting']['kropff']['low']['bhkl']

			metadata = ["# Bragg peak fitting of row {}".format(row_selected)]
			metadata.append("# x0: {}".format(x0))
			metadata.append("# y0: {}".format(y0))
			metadata.append("# width: {}".format(width))
			metadata.append("# height: {}".format(height))
			metadata.append("# a0: {}".format(a0))
			metadata.append("# b0: {}".format(b0))
			metadata.append("# ahkl: {}".format(ahkl))
			metadata.append("# bhkl: {}".format(bhkl))
			metadata.append("#")
			metadata.append("# tof (micros), average counts")

			make_ascii_file_from_2dim_array(metadata=metadata,
			                                col1=x_axis,
			                                col2=y_axis,
			                                output_file_name=full_file_name)

			message = "Output file {}".format(full_file_name)
			self.parent.ui.statusbar.showMessage(message, 15000)   # 15s
			self.parent.ui.statusbar.setStyleSheet("color: green")
