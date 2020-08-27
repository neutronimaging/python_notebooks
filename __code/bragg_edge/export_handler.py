from pathlib import Path
from qtpy.QtWidgets import QFileDialog
import numpy as np
from collections import OrderedDict

from __code.bragg_edge.get import Get
from __code.file_handler import make_ascii_file
from __code.bragg_edge.bragg_edge_peak_fitting_gui_utility import GuiUtility


class ExportHandler:

	def __init__(self, parent=None):
		self.parent = parent

	def configuration(self):
		# bring file dialog to locate where the file will be saved
		base_folder = Path(self.parent.working_dir)
		directory = str(base_folder.parent)
		_export_folder = QFileDialog.getExistingDirectory(self.parent,
		                                                  directory=directory,
		                                                  caption="Select Output Folder",
		                                                  options=QFileDialog.ShowDirsOnly)

		if _export_folder:
			data, metadata = self.get_data_metadata_from_selection_tab()

			# collect initial selection size (x0, y0, width, height)
			o_get = Get(parent=self.parent)
			[x0, y0, x1, y1, width, height] = o_get.selection_roi_dimension()

			name_of_ascii_file = ExportHandler.makeup_name_of_profile_ascii_file(base_name=str(base_folder.name),
			                                                                     export_folder=_export_folder,
			                                                                     x0=x0, y0=y0,
			                                                                     width=width,
			                                                                     height=height)

			make_ascii_file(metadata=metadata,
			                data=data,
			                output_file_name=name_of_ascii_file,
			                dim='1d')

			self.parent.ui.statusbar.showMessage("{} has been created!".format(name_of_ascii_file), 10000)  # 10s
			self.parent.ui.statusbar.setStyleSheet("color: green")

	@staticmethod
	def makeup_name_of_profile_ascii_file(base_name="default",
	                                      export_folder="./",
	                                      x0=None, y0=None, width=None, height=None):
		"""this will return the full path name of the ascii file to create that will contain all the profiles
		starting with the selection box and all the way to the minimal size"""
		full_base_name = "full_set_of_shrinkable_region_profiles_from_" + \
		                 "x{}_y{}_w{}_h{}_for_folder_{}.txt".format(x0, y0, width, height, base_name)
		return str(Path(export_folder) / full_base_name)

	def get_data_metadata_from_selection_tab(self):
		base_folder = Path(self.parent.working_dir)
		o_get = Get(parent=self.parent)

		index_axis, _ = o_get.specified_x_axis(xaxis='index')
		tof_axis, _ = o_get.specified_x_axis(xaxis='tof')
		lambda_axis, _ = o_get.specified_x_axis('lambda')
		fitting_peak_range = self.parent.bragg_edge_range
		distance_detector_sample = str(self.parent.ui.distance_detector_sample.text())
		detector_offset = str(self.parent.ui.detector_offset.text())
		kropff_fitting_values = self.collect_all_kropff_fitting_values()
		march_dollase_fitting_values = self.collect_all_march_dollase_fitting_values()

		dict_regions = o_get.all_russian_doll_region_full_infos()
		metadata = ExportHandler.make_metadata(base_folder=base_folder,
		                                       fitting_peak_range=fitting_peak_range,
		                                       dict_regions=dict_regions,
		                                       distance_detector_sample=distance_detector_sample,
		                                       detector_offset=detector_offset,
		                                       kropff_fitting_values=kropff_fitting_values,
		                                       march_dollase_fitting_values=march_dollase_fitting_values)
		self.add_fitting_infos_to_metadata(metadata)

		metadata.append("#")
		metadata.append("#File Index, TOF(micros), lambda(Angstroms), ROIs (see above)")
		data = ExportHandler.format_data(col1=index_axis,
		                                 col2=tof_axis,
		                                 col3=lambda_axis,
		                                 dict_regions=dict_regions)

		return data, metadata

	def add_fitting_infos_to_metadata(self, metadata):
		o_tab = GuiUtility(parent=self.parent)
		fitting_algorithm_used = o_tab.get_tab_selected(tab_ui=self.parent.ui.tab_algorithm)
		# fitting_rois = self.fitting_rois
		fitting_flag = True if self.parent.fitting_peak_ui else False
		metadata.append("#fitting procedure started: {}".format(fitting_flag))
		metadata.append("#fitting algorithm selected: {}".format(fitting_algorithm_used))
		# kropff
		for _key in self.parent.kropff_fitting_range.keys():
			metadata.append("#kropff {} selection range: [{}, {}]".format(_key,
			                                                              self.parent.kropff_fitting_range[_key][0],
			                                                              self.parent.kropff_fitting_range[_key][1]))

		# March-dollase
		for _row_index, _row_entry in enumerate(self.parent.march_dollase_fitting_history_table):
			str_row_entry = [str(_value) for _value in _row_entry]
			joined_str_row_entry = ", ".join(str_row_entry)
			metadata.append("#marche-dollase history table row {}: {}".format(_row_index, joined_str_row_entry))

		[d_spacing, sigma, alpha, a1, a2, a5, a6] = self.parent.march_dollase_fitting_initial_parameters
		metadata.append("#marche-dollase history init d_spacing: {}".format(d_spacing))
		metadata.append("#marche-dollase history init sigma: {}".format(sigma))
		metadata.append("#marche-dollase history init alpha: {}".format(alpha))
		metadata.append("#marche-dollase history init a1: {}".format(a1))
		metadata.append("#marche-dollase history init a2: {}".format(a2))
		metadata.append("#marche-dollase history init a5: {}".format(a5))
		metadata.append("#marche-dollase history init a6: {}".format(a6))

	def collect_all_march_dollase_fitting_values(self):
		march_fitting_values = OrderedDict()
		fitting_input_dictionary = self.parent.fitting_input_dictionary

		for _row in fitting_input_dictionary['rois'].keys():
			_entry = fitting_input_dictionary['rois'][_row]['fitting']['march_dollase']

			march_fitting_values[_row] = {'d_spacing': _entry['d_spacing'],
			                              'sigma': _entry['sigma'],
			                              'alpha': _entry['alpha'],
			                              'a1': _entry['a1'],
			                              'a2': _entry['a2'],
			                              'a5': _entry['a5'],
			                              'a6': _entry['a6'],
			                              'd_spacing_error': _entry['d_spacing_error'],
			                              'sigma_error': _entry['sigma_error'],
			                              'alpha_error': _entry['alpha_error'],
			                              'a1_error': _entry['a1_error'],
			                              'a2_error': _entry['a2_error'],
			                              'a5_error': _entry['a5_error'],
			                              'a6_error': _entry['a6_error'],
			                               }
		return march_fitting_values

	def collect_all_kropff_fitting_values(self):
		kropff_fitting_values = OrderedDict()

		fitting_input_dictionary = self.parent.fitting_input_dictionary

		for _row in fitting_input_dictionary['rois'].keys():
			_entry = fitting_input_dictionary['rois'][_row]['fitting']['kropff']

			_entry_high = _entry['high']
			_entry_low = _entry['low']
			_entry_bragg_peak = _entry['bragg_peak']
			kropff_fitting_values[_row] = {'a0': _entry_high['a0'],
			                               'b0': _entry_high['b0'],
			                               'a0_error': _entry_high['a0_error'],
			                               'b0_error': _entry_high['b0_error'],
			                               'ahkl': _entry_low['ahkl'],
			                               'bhkl': _entry_low['bhkl'],
			                               'ahkl_error': _entry_low['ahkl_error'],
			                               'bhkl_error': _entry_low['bhkl_error'],
			                               'tofhkl': _entry_bragg_peak['tofhkl'],
			                               'tau': _entry_bragg_peak['tau'],
			                               'sigma': _entry_bragg_peak['sigma'],
			                               'tofhkl_error': _entry_bragg_peak['tofhkl_error'],
			                               'tau_error': _entry_bragg_peak['tau_error'],
			                               'sigma_error': _entry_bragg_peak['sigma_error'],
			                               }
		return kropff_fitting_values

	@staticmethod
	def make_metadata(base_folder=None,
	                  fitting_peak_range=None,
	                  dict_regions=None,
	                  distance_detector_sample="",
	                  detector_offset="",
	                  kropff_fitting_values=None,
	                  march_dollase_fitting_values=None):

		metadata = ["#base folder: {}".format(base_folder)]
		metadata.append("#fitting peak range in file index: [{}, {}]".format(fitting_peak_range[0],
		                                                                     fitting_peak_range[1]))
		metadata.append("#distance detector-sample: {}".format(distance_detector_sample))
		metadata.append("#detector offset: {}".format(detector_offset))
		for _row, _key in enumerate(dict_regions.keys()):
			_entry = dict_regions[_key]
			x0 = _entry['x0']
			y0 = _entry['y0']
			width = _entry['width']
			height = _entry['height']

			_entry_kropff = kropff_fitting_values[_row]
			a0 = _entry_kropff['a0']
			b0 = _entry_kropff['b0']
			a0_error = _entry_kropff['a0_error']
			b0_error = _entry_kropff['b0_error']
			ahkl = _entry_kropff['ahkl']
			bhkl = _entry_kropff['bhkl']
			ahkl_error = _entry_kropff['ahkl_error']
			bhkl_error = _entry_kropff['bhkl_error']
			tofhkl = _entry_kropff['tofhkl']
			tau = _entry_kropff['tau']
			sigma = _entry_kropff['sigma']
			tofhkl_error = _entry_kropff['tofhkl_error']
			tau_error = _entry_kropff['tau_error']
			sigma_error = _entry_kropff['sigma_error']

			_entry_march = march_dollase_fitting_values[_row]
			d_spacing = _entry_march['d_spacing']
			sigma1 = _entry_march['sigma']
			alpha = _entry_march['alpha']
			a1 = _entry_march['a1']
			a2 = _entry_march['a2']
			a5 = _entry_march['a5']
			a6 = _entry_march['a6']
			d_spacing_error = _entry_march['d_spacing_error']
			sigma1_error = _entry_march['sigma_error']
			alpha_error = _entry_march['alpha_error']
			a1_error = _entry_march['a1_error']
			a2_error = _entry_march['a2_error']
			a5_error = _entry_march['a5_error']
			a6_error = _entry_march['a6_error']

			metadata.append("#column {} -> x0:{}, y0:{}, width:{}, height:{},"
			                " kropff: a0:{}, b0:{}, a0_error:{}, b0_error:{},"
			                " ahkl:{}, bhkl:{}, ahkl_error:{}, bhkl_error:{},"
			                " tofhkl:{}, tau:{}, sigma:{},"
			                " tofhkl_error:{}, tau_error:{}, sigma_error:{},"
			                " march_dollase: d_spacing:{}, sigma:{}, alpha:{},"
			                " a1:{}, a2:{}, a5:{}, a6:{},"
			                " d_spacing_error:{}, sigma_error:{}, alpha_error:{},"
			                " a1_error:{}, a2_error:{}, a5_error:{}, a6_error:{}".format(_key + 3,
			                                                                            x0, y0,
			                                                                            width, height,
			                                                                            a0, b0, a0_error, b0_error,
			                                                                            ahkl, bhkl,
			                                                                            ahkl_error,
			                                                                            bhkl_error,
			                                                                            tofhkl, tau, sigma,
			                                                                            tofhkl_error,
			                                                                            tau_error,
			                                                                            sigma_error,
			                                                                            d_spacing,
			                                                                            sigma1, alpha,
			                                                                            a1, a2, a5, a6,
			                                                                            d_spacing_error,
			                                                                            sigma1_error, alpha_error,
			                                                                            a1_error, a2_error, a5_error,
			                                                                            a6_error))

		return metadata

	@staticmethod
	def format_data(col1=None, col2=None, col3=None, dict_regions=None):
		if col1 is None:
			return []

		data = []
		profile_length = len(dict_regions[0]['profile'])
		for _row_index in np.arange(profile_length):
			list_profile_for_this_row = []
			for _key in dict_regions.keys():
				_profile = dict_regions[_key]['profile']
				list_profile_for_this_row.append(str(_profile[_row_index]))
			_col1 = col1[_row_index]
			_col2 = col2[_row_index]
			_col3 = col3[_row_index]
			data.append("{}, {}, {}, ".format(_col1, _col2, _col3) + ", ".join(list_profile_for_this_row))
		return data

