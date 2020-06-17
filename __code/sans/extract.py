import os
import copy
import h5py
from pathlib import Path
from ipywidgets import widgets
from IPython.core.display import display
from IPython.core.display import HTML
from collections import OrderedDict
import numpy as np

from __code import fileselector
from __code.nexus_handler import get_list_entries, get_entry_value
from __code.file_folder_browser import FileFolderBrowser
from __code.time_utility import AbsoluteTimeHandler, RelativeTimeHandler
from __code.interpolation_utilities import Interpolation
from __code.sans.sans_config import gpsans_parameters, biosans_parameters

STARTING_ENTRIES = ['entry', 'DASlogs']
LIST_SANS_INSTRUMENTS = {'GP-SANS (CG2)': {'unix_name': 'CG2'},
                         'BIO-SANS (CG3)': {'unix_name': 'CG3'}}


class Initializer:

	def select_instrument(self):
		list_instruments = list(LIST_SANS_INSTRUMENTS.keys())
		instrument_ui = widgets.HBox([widgets.Label("Select your instrument",
			                                        layout=widgets.Layout(width='15%')),
		                              widgets.Select(options=list_instruments,
		                                             layout=widgets.Layout(width='30%',
		                                                                   height='50px'))])
		display(instrument_ui)
		self.instrument_list_ui = instrument_ui.children[1]

	def get_working_dir(self):
		instrument_name = self.instrument_list_ui.value
		short_name = LIST_SANS_INSTRUMENTS[instrument_name]['unix_name']
		full_path = f'/HFIR/{short_name}/'
		return full_path

	def get_instrument(self):
		return self.instrument_list_ui.value


class Extract(FileFolderBrowser):

	first_nexus_selected = ''
	widget_height = "400px"
	full_list_selected = {}

	def __init__(self, working_dir="./", instrument='GP-SANS (CG2)'):
		self.instrument = Extract.get_short_version_instrument(instrument)
		super(Extract, self).__init__(working_dir=working_dir)

		if self.instrument == 'CG2':
			self.list_parameters = gpsans_parameters
		else:
			self.list_parameters = biosans_parameters

		self.init_full_list_selected()

	def init_full_list_selected(self):
		for para in self.list_parameters.keys():
			self.full_list_selected[para] = []

	@staticmethod
	def get_short_version_instrument(instrument):
		if 'CG2' in instrument:
			return 'CG2'
		else:
			return 'CG3'

	def select_reductionlog(self):
		self.o_file = fileselector.FileSelectorPanelWithJumpFolders(start_dir=self.working_dir,
		                                                            instruction="Select ReductionLog files",
		                                                            type='file',
		                                                            multiple=True,
		                                                            next=self.display_metadata,
		                                                            filters={'reductionLog': "*_reduction_log.hdf"},
		                                                            default_filter='reductionLog',
		                                                            show_jump_to_share=False)

	def display_metadata(self, list_nexus):

		self.o_file.shortcut_buttons.close()
		self.list_nexus = list_nexus

		self.list_keys = self.retrieve_left_widget_list_keys()
		self.list_values = self.retrieve_right_widget_list_keys(left_widget_key_selected=list(self.list_keys)[0])

		# search box
		search_box = widgets.HBox([widgets.Label("Search:"),
		                           widgets.Text("",
		                                        layout=widgets.Layout(width="30%"))])
		# search_text_widget = search_box.children[1]
		# search_text_widget.observe(self.search_text_changed, names='value')

		# list of keys
		hori_box = widgets.HBox([widgets.Select(options=self.list_keys,
	                                            layout=widgets.Layout(width="400px",
	                                                                  height=self.widget_height)),
		                         widgets.SelectMultiple(options=self.list_values,
		                                        layout=widgets.Layout(width="400px",
		                                                              height=self.widget_height))],
	                             )
		display(hori_box)
		[self.left_widget_ui, self.right_widget_ui] = hori_box.children
		self.left_widget_ui.observe(self.left_widget_changed, names='value')
		self.right_widget_ui.observe(self.right_widget_changed, names='value')

		display(widgets.Label("Command + Click: to select more than 1 element in the right widget"))

	def left_widget_changed(self, new_value):
		value_selected = new_value['new']
		right_value = self.list_parameters[value_selected]['list']
		self.right_widget_ui.options = right_value
		self.right_widget_ui.value = self.full_list_selected[value_selected]

	def get_left_widget_selected(self):
		value_selected = self.left_widget_ui.value
		return value_selected

	def right_widget_changed(self, new_value):
		list_new_value_selected = new_value['new']
		left_widget_value = self.get_left_widget_selected()
		self.full_list_selected[left_widget_value] = list_new_value_selected

	def retrieve_left_widget_list_keys(self):
		return self.list_parameters.keys()

	def retrieve_right_widget_list_keys(self, left_widget_key_selected=None):
		if left_widget_key_selected is None:
			left_widget_key_selected = self.left_widget_ui.value
		return self.list_parameters[left_widget_key_selected]['list']

	def search_text_changed(self, value):
		pass
		# new_text = value['new']
		# if new_text == "":
		# 	self.top_keys_widgets.value = self.list_daslogs_keys[0]
		# 	return
		#
		# for key in self.list_daslogs_keys:
		# 	if new_text in key:
		# 		self.top_keys_widgets.value = key
		# 		return

	def select_metadata(self, list_nexus=None):
		if list_nexus is None:
			return

		self.list_nexus = list_nexus

		self.first_nexus_selected = list_nexus[0]
		self.dict_daslogs_keys = get_list_entries(nexus_file_name=self.first_nexus_selected,
		                                          starting_entries=STARTING_ENTRIES)

		self.display_widgets()

	def extract_all(self, output_folder):
		list_nexus = self.list_nexus
		for _nexus in list_nexus:
			self.extract(nexus_file_name=_nexus,
			             output_folder=output_folder)

	def makeup_output_file_name(self, nexus_file_name='', output_folder='./'):
		short_nexus_file_name = os.path.basename(nexus_file_name)
		base_name, ext = os.path.splitext(short_nexus_file_name)
		new_name = str(Path(output_folder) / "{}_extracted.txt".format(base_name))
		return new_name

	def get_entry_value(self, nexus_file_name=None, entry_path=None):
		'''

		:param nexus_file_name: hdf5 full file path
		:param entry_path: full path through the file to retrieve the information
			example: ['entry', 'DASlogs', 'PV1', 'value']
		:return: value at the given path in the hdf5 file
		'''
		if nexus_file_name is None:
			raise ValueError("Please provide a full path to a nexus file name!")

		if not Path(nexus_file_name).exists():
			raise ValueError("File do not exist!")

		with h5py.File(nexus_file_name, 'r') as nxs:

			try:
				nxs_path = nxs
				for _item in entry_path:
					nxs_path = nxs_path.get(_item)
			except AttributeError:
				raise AttributeError("Path specify in the HDF5 is wrong!")

			if nxs_path is None:
				return None

			return nxs_path[()]


	def extract(self, nexus_file_name='', output_folder='./'):

		full_list_selected = self.full_list_selected

		metadata = ['# nexus file name: ' + nexus_file_name]
		metadata = ['#']
		data = []

		for top_key in full_list_selected.keys():
			top_path = self.list_parameters[top_key]['path']
			for internal_key in full_list_selected[top_key]:
				metadata = [f'# {top_key} -> {internal_key}']
				entry_path = copy.deepcopy(top_path)
				entry_path.append(internal_key)

				# print(f"top_key: {top_key}")
				# print(f"top_path: {top_path}")
				# print(f"metadata: {metadata}")
				print(f"entry_path: {entry_path}")

				value = self.get_entry_value(nexus_file_name=nexus_file_name,
			                            entry_path=entry_path)

				print(f"value: {value}")



		output_file_name = self.makeup_output_file_name(nexus_file_name=nexus_file_name,
		                                                output_folder=output_folder)
		print(f"output file will be {output_file_name}")
		# # Extract.create_output_file(file_name=output_file_name,
		# #                            dictionary=final_dict)

		return







		top_entry_path = copy.deepcopy(STARTING_ENTRIES)
		top_entry_path.append(top_key_widget_value)

		x_axis_entry_path = copy.deepcopy(top_entry_path)
		x_axis_entry_path.append(x_axis_key)

		x_axis_array = get_entry_value(nexus_file_name=nexus_file_name,
		                               entry_path=x_axis_entry_path)
		y_axis_entry_path = copy.deepcopy(top_entry_path)
		y_axis_entry_path.append(y_axis_key)
		y_axis_array = get_entry_value(nexus_file_name=nexus_file_name,
		                               entry_path=y_axis_entry_path)

		if interpolate_flag:

			if len(x_axis_array) == 1:
				return None

			x_min = int(x_axis_array[0]/interpolate_increment_value)
			if x_min != x_axis_array[0]:
				x_min += interpolate_increment_value

			new_x_axis_array = np.arange(x_min, x_axis_array[-1], interpolate_increment_value)
			o_interpolation = Interpolation(x_axis=x_axis_array,
		                                    y_axis=y_axis_array)

			try:
				y_axis_array = o_interpolation.get_new_y_array(new_x_axis=new_x_axis_array)
			except TypeError:
				return None

			x_axis_array = new_x_axis_array

		col3 = {'data': None,
		        'name': 'absolute time'}
		col4 = {'data': None,
		        'name': 'master relative time (s)'}
		col_legend = "{}, {}".format(x_axis_key, y_axis_key)
		if use_absolute_time_offset:
			starting_time = get_entry_value(nexus_file_name=nexus_file_name,
		                                    entry_path=['entry','start_time'])
			starting_time = starting_time[0].decode('UTF-8')
			metadata.append("# starting time of this file: {}".format(starting_time))

			master_starting_time = get_entry_value(nexus_file_name=self.first_nexus_selected,
			                                entry_path=['entry', 'start_time'])
			master_starting_time = master_starting_time[0].decode('UTF-8')
			metadata.append("# starting time of first file: {}".format(master_starting_time))

			if x_axis_key == 'time':
				time_axis = x_axis_array
			else:
				time_axis = y_axis_array

			o_absolute = AbsoluteTimeHandler(initial_absolute_time=starting_time[0])
			absolute_time_axis = o_absolute.get_absolute_time_for_this_delta_time_array(delta_time_array=time_axis)
			col3['data'] = absolute_time_axis
			col_legend += ", {}".format('absolute time')

			o_relative = RelativeTimeHandler(master_initial_time=master_starting_time,
			                                 local_initial_time=starting_time)
			master_relative_time_axis = o_relative.get_relative_time_for_this_time_array(time_array=time_axis)
			col4['data'] = master_relative_time_axis
			col_legend += ", {}".format('master relative time (s)')

		metadata.append("#")
		metadata.append("# {}".format(col_legend))


	def export(self):
		self.output_folder_ui = fileselector.FileSelectorPanelWithJumpFolders(
				instruction='select where to create the ' + \
				            'ascii file',
				start_dir=self.working_dir,
				next=self.extract_all,
				type='directory',
				newdir_toolbar_button=True,
				show_jump_to_share=False)

	@staticmethod
	def create_output_file(file_name=None, dictionary=None):

		if len(dictionary) == 0:
			display(HTML('<span style="font-size: 20px; color:red">No ASCII file has been created!</span>'))
			return

		with open(file_name, 'w') as f:

			for _key in dictionary.keys():
				item = dictionary[_key]

				_metadata = item['metadata']
				for _line in _metadata:
					_line += "\n"
					f.write(_line)

				item_col1 = item['col1']['data']
				item_col2 = item['col2']['data']
				item_col3 = item['col3']['data']
				item_col4 = item['col4']['data']

				for _index in np.arange(len(item['col1']['data'])):
					_line = "{}, {}".format(item_col1[_index], item_col2[_index])
					if item_col3:
						_line += ", {}, {}".format(item_col3[_index], item_col4[_index])
					_line += "\n"
					f.write(_line)

				f.write("\n")

		display(HTML('<span style="font-size: 20px; color:blue">The following ASCII file has been created: ' +
		             '</span><span style="font-size: 20px; color:green">' + file_name + '</span>'))
