import numpy as np
from qtpy import QtGui
from qtpy.QtWidgets import QFileDialog
from pathlib import Path
import pyqtgraph as pg

from __code.table_handler import TableHandler
from __code.bragg_edge.bragg_edge_peak_fitting_gui_utility import GuiUtility
from __code.bragg_edge.kropff_fitting_job_handler import KropffFittingJobHandler
from __code.file_handler import make_ascii_file_from_2dim_array
from __code.bragg_edge.get import Get
from __code._utilities.dictionary import key_path_exists_in_dictionary


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

		selected_rows_submenu = QtGui.QMenu("Selected Rows")
		menu.addMenu(selected_rows_submenu)
		_fit = selected_rows_submenu.addAction("Fit")
		_export = selected_rows_submenu.addAction("Export ...")

		advanced_selection_submenu = QtGui.QMenu("Advanced Rows Selection")
		menu.addMenu(advanced_selection_submenu)
		_negative_thkl = advanced_selection_submenu.addAction("Where t_hkl < 0")

		action = menu.exec_(QtGui.QCursor.pos())

		if action == _fit:
			self.fit_bragg_peak_selected_rows()
		elif action == _export:
			self.export_bragg_peak_profile()
		elif action == _negative_thkl:
			self.select_all_rows_with_negative_thkl()

		QtGui.QGuiApplication.processEvents()  # to close QFileDialog

	def fit_bragg_peak_selected_rows(self):
		o_gui = GuiUtility(parent=self.parent)
		list_rows_selected = o_gui.get_rows_of_table_selected(table_ui=self.parent.ui.bragg_edge_tableWidget)
		self.parent.kropff_fit_bragg_peak_region_of_selected_rows(list_row_to_fit=list_rows_selected)

	def export_bragg_peak_profile(self):
		working_dir = str(Path(self.parent.working_dir).parent)
		_export_folder = QFileDialog.getExistingDirectory(self.parent,
		                                                  directory=working_dir,
		                                                  caption="Select Output Folder")

		QtGui.QGuiApplication.processEvents()  # to close QFileDialog

		if _export_folder:

			o_gui = GuiUtility(parent=self.parent)
			list_row_selected = o_gui.get_rows_of_table_selected(table_ui=self.parent.ui.bragg_edge_tableWidget)

			for row_selected in list_row_selected:

				# make up output file name
				name_of_row = o_gui.get_table_str_item(table_ui=self.parent.ui.bragg_edge_tableWidget,
				                                       row=row_selected,
				                                       column=0)
				[x0, y0, width, height] = name_of_row.split("; ")
				name_of_row_formatted = "x0{}_y0{}_width{}_height{}".format(x0,y0, width, height)
				file_name = "kropff_bragg_peak_profile_{}.txt".format(name_of_row_formatted)
				full_file_name = str(Path(_export_folder) / Path(file_name))

				o_fit = KropffFittingJobHandler(parent=self.parent)
				o_fit.prepare(kropff_tooldbox='bragg_peak')

				x_axis = o_fit.xaxis_to_fit
				y_axis = o_fit.list_yaxis_to_fit[row_selected]

				a0 = self.parent.fitting_input_dictionary['rois'][row_selected]['fitting']['kropff']['high']['a0']
				b0 = self.parent.fitting_input_dictionary['rois'][row_selected]['fitting']['kropff']['high']['b0']
				ahkl = self.parent.fitting_input_dictionary['rois'][row_selected]['fitting']['kropff']['low']['ahkl']
				bhkl = self.parent.fitting_input_dictionary['rois'][row_selected]['fitting']['kropff']['low']['bhkl']

				metadata = ["# Bragg peak fitting of row {}".format(row_selected+1)]
				metadata.append("# x0: {}".format(x0))
				metadata.append("# y0: {}".format(y0))
				metadata.append("# width: {}".format(width))
				metadata.append("# height: {}".format(height))
				metadata.append("# a0: {}".format(a0))
				metadata.append("# b0: {}".format(b0))
				metadata.append("# ahkl: {}".format(ahkl))
				metadata.append("# bhkl: {}".format(bhkl))
				metadata.append("#")
				metadata.append("# tof (micros), average transimission")

				make_ascii_file_from_2dim_array(metadata=metadata,
				                                col1=x_axis,
				                                col2=y_axis,
				                                output_file_name=full_file_name)

			message = "Exported {} file(s) in {}".format(len(list_row_selected), _export_folder)
			self.parent.ui.statusbar.showMessage(message, 15000)   # 15s
			self.parent.ui.statusbar.setStyleSheet("color: green")

	def select_all_rows_with_negative_thkl(self):
		# activate table
		self.parent.ui.bragg_edge_tableWidget.setFocus()

		# switch to multi selection mode
		self.parent.ui.kropff_bragg_peak_multi_selection.setChecked(True)
		self.parent.ui.bragg_edge_tableWidget.setSelectionMode(2)

		list_of_rows_to_select = []
		fitting_input_dictionary_rois = self.parent.fitting_input_dictionary['rois']
		for _row in fitting_input_dictionary_rois.keys():
			_thkl = np.float(fitting_input_dictionary_rois[_row]['fitting']['kropff']['bragg_peak']['tofhkl'])
			if _thkl < 0:
				list_of_rows_to_select.append(_row)

		o_gui = GuiUtility(parent=self.parent)
		o_gui.select_rows_of_table(table_ui=self.parent.ui.bragg_edge_tableWidget,
		                           list_of_rows=list_of_rows_to_select)

	def update_fitting_plot(self):
		self.parent.ui.fitting.clear()
		o_get = Get(parent=self.parent)
		part_of_fitting_dict = o_get.part_of_fitting_selected()
		name_of_page = part_of_fitting_dict['name_of_page']
		table_ui = part_of_fitting_dict['table_ui']

		o_table = TableHandler(table_ui=table_ui)
		list_row_selected = o_table.get_rows_of_table_selected()
		x_axis_selected = o_get.x_axis_checked()

		if list_row_selected is None:
			# first fitting tab where we only display the full data with bragg peak selection
			if self.parent.fitting_peak_ui:
				self.parent.ui.fitting.removeItem(self.parent.fitting_peak_ui)
			xaxis_dict = self.parent.fitting_input_dictionary['xaxis']
			xaxis_index, xaxis_label = xaxis_dict[x_axis_selected]
			[left_xaxis_index, right_xaxis_index] = self.parent.bragg_edge_range
			xaxis = xaxis_index[left_xaxis_index: right_xaxis_index]
			selected_roi = self.parent.fitting_input_dictionary['rois'][0]
			yaxis = selected_roi['profile']
			yaxis = yaxis[left_xaxis_index: right_xaxis_index]
			self.parent.ui.fitting.plot(xaxis, -np.log(yaxis), pen=(self.parent.selection_roi_rgb[0],
			                                                 self.parent.selection_roi_rgb[1],
			                                                 self.parent.selection_roi_rgb[2]),
			                     symbol='o')
			peak_range_index = self.parent.kropff_fitting_range['bragg_peak']
			if peak_range_index[0] is None:
				peak_range = self.parent.bragg_edge_range
			else:
				peak_range = [xaxis[peak_range_index[0]], xaxis[peak_range_index[1]]]

			if self.parent.fitting_peak_ui:
				self.parent.ui.fitting.removeItem(self.parent.fitting_peak_ui)
			self.parent.fitting_peak_ui = pg.LinearRegionItem(values=peak_range,
			                                           orientation=None,
			                                           brush=None,
			                                           movable=True,
			                                           bounds=None)
			self.parent.fitting_peak_ui.sigRegionChanged.connect(self.parent.fitting_range_changed)
			self.parent.fitting_peak_ui.setZValue(-10)
			self.parent.ui.fitting.addItem(self.parent.fitting_peak_ui)

		else:

			for row_selected in list_row_selected:

				selected_roi = self.parent.fitting_input_dictionary['rois'][row_selected]

				xaxis_dict = self.parent.fitting_input_dictionary['xaxis']
				[left_xaxis_index, right_xaxis_index] = self.parent.bragg_edge_range

				yaxis = selected_roi['profile']
				xaxis_index, xaxis_label = xaxis_dict[x_axis_selected]

				xaxis = xaxis_index[left_xaxis_index: right_xaxis_index]
				yaxis = yaxis[left_xaxis_index: right_xaxis_index]

				self.parent.ui.fitting.setLabel("bottom", xaxis_label)
				self.parent.ui.fitting.setLabel("left", 'Cross Section (arbitrary units)')
				self.parent.ui.fitting.plot(xaxis, -np.log(yaxis), pen=(self.parent.selection_roi_rgb[0],
				                                                 self.parent.selection_roi_rgb[1],
				                                                 self.parent.selection_roi_rgb[2]),
				                     symbol='o')

				peak_range_index = self.parent.kropff_fitting_range[name_of_page]
				if peak_range_index[0] is None:
					peak_range = self.parent.bragg_edge_range
				else:
					peak_range = [xaxis[peak_range_index[0]], xaxis[peak_range_index[1]]]

				if self.parent.fitting_peak_ui:
					self.parent.ui.fitting.removeItem(self.parent.fitting_peak_ui)
				self.parent.fitting_peak_ui = pg.LinearRegionItem(values=peak_range,
				                                           orientation=None,
				                                           brush=None,
				                                           movable=False,
				                                           bounds=None)
				self.parent.fitting_peak_ui.sigRegionChanged.connect(self.parent.fitting_range_changed)
				self.parent.fitting_peak_ui.setZValue(-10)
				self.parent.ui.fitting.addItem(self.parent.fitting_peak_ui)

				o_gui = GuiUtility(parent=self.parent)
				algo_name = o_gui.get_tab_selected(self.parent.ui.tab_algorithm).lower()

				if key_path_exists_in_dictionary(dictionary=self.parent.fitting_input_dictionary,
				                                 tree_key=['rois', row_selected, 'fitting', algo_name,
				                                           name_of_page, 'xaxis_to_fit']):

					# show fit only if tof scale selected
					if x_axis_selected == 'tof':
						_entry = self.parent.fitting_input_dictionary['rois'][row_selected]['fitting'][algo_name][name_of_page]
						xaxis = _entry['xaxis_to_fit']
						yaxis = _entry['yaxis_fitted']
						# yaxis = -np.log(yaxis)
						self.parent.ui.fitting.plot(xaxis, yaxis, pen=(self.parent.fit_rgb[0],
						                                               self.parent.fit_rgb[1],
						                                               self.parent.fit_rgb[2]))

				if peak_range_index[0] is None:
					self.parent.fitting_range_changed()