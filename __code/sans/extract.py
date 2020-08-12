import os
import copy
import h5py
from pathlib import Path
from ipywidgets import widgets
from IPython.core.display import display, clear_output
from IPython.core.display import HTML
from collections import OrderedDict
import numpy as np

from __code import fileselector
from __code.nexus_handler import get_list_entries
from __code.file_folder_browser import FileFolderBrowser
from __code.sans.sans_config import gpsans_parameters, biosans_parameters
from __code.file_handler import make_ascii_file

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
		full_path = '/HFIR/{}/'.format(short_name)
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
		self.list_nexus = None

	def init_full_list_selected(self):
		for para in self.list_parameters.keys():
			self.full_list_selected[para] = []

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

	def select_metadata(self, list_nexus=None):
		if list_nexus is None:
			return

		self.list_nexus = list_nexus

		self.first_nexus_selected = list_nexus[0]
		self.dict_daslogs_keys = get_list_entries(nexus_file_name=self.first_nexus_selected,
		                                          starting_entries=STARTING_ENTRIES)

		self.display_widgets()

	def export(self):
		self.output_folder_ui = fileselector.FileSelectorPanelWithJumpFolders(
				instruction='select where to create the ' + \
				            'ascii file',
				start_dir=self.working_dir,
				next=self.extract_all_in_one,
				type='directory',
				newdir_toolbar_button=True,
				show_jump_to_share=False)

	@staticmethod
	def reformat_dict(full_dict):
		'''
		we need to go from {'nexus1': {'path1': value1', 'path2': value2},
		 ...}
		to
		{'path1': {'nexus1': value1, 'nexus2': value2},
		 ...}
		'''
		new_full_dict = OrderedDict()
		for _nexus_key in full_dict.keys():
			for _path_key in full_dict[_nexus_key].keys():
				_value = full_dict[_nexus_key][_path_key]
				if not (_path_key in new_full_dict.keys()):
					new_full_dict[_path_key] = OrderedDict()
				new_full_dict[_path_key][_nexus_key] = _value

		return new_full_dict

	def extract_all_in_one(self, output_folder):

		display(HTML('<span style="font-size: 20px; color:blue">Work in progress ... </span>'))

		self.output_folder_ui.shortcut_buttons.close()
		output_file_name = Extract.create_output_file_name(output_folder=output_folder,
		                                                nbr_nexus=len(self.list_nexus))
		full_list_selected = self.full_list_selected

		# get list of path
		list_entry_path = []
		for top_key in full_list_selected.keys():
			top_path = copy.deepcopy(self.list_parameters[top_key]['path'])
			for inside_key in full_list_selected[top_key]:
				full_path = copy.deepcopy(top_path)
				full_path.append(inside_key)
				# metadata_tag = "# {} -> {}".format(top_key, inside_key)
				list_entry_path.append(full_path)

		list_nexus = self.list_nexus
		metadata = []
		label_of_columns = []
		for _index, _nexus in enumerate(list_nexus):
			_line = [_nexus]

			if _index == 0:
				label_of_columns.append("nexus name")
			reduction_log_dict = Extract.get_entry_value(nexus_file_name=_nexus,
			                                             list_entry_path=list_entry_path)
			for _key in reduction_log_dict.keys():
				_value = reduction_log_dict[_key]
				# print(f"-> _key:{_key}: {_value}")
				# print(f"--> type(_value): {type(_value)}")

				if type(_value) is str:
					if _index == 0:
						label_of_columns.append(_key)
					_line.append(_value)
				elif type(_value) is list:
					if _index == 0:
						label_of_columns.append(_key)
					array_value = np.array(_value)
					_line.append("{}".format(np.mean(array_value)))
				elif type(_value) is dict:
					for _inside_key in _value.keys():
						if _index == 0:
							label_of_columns.append("{}/{}".format(_key, _inside_key))
						_line.append("{}".format(np.mean(_value[_inside_key])))

			metadata.append(", ".join(_line))

		label_of_columns = ", ".join(label_of_columns)

		final_metadata = [label_of_columns]
		for _meta in metadata:
			final_metadata.append(_meta)

		make_ascii_file(metadata=final_metadata,
		                output_file_name=output_file_name)

		clear_output(wait=False)
		display(HTML('<span style="font-size: 20px; color:blue">The following ASCII file has been created: ' +
		             '</span><span style="font-size: 20px; color:green">' + output_file_name + '</span>'))

	@staticmethod
	def update_metadata(list_metadata, metadata):

		if type(list_metadata[0]) == list:

			# get the first element of each array, then the second of each array ...
			index = 0
			while index < len(list_metadata[0]):
				line = []
				for _array in list_metadata:
					if index > (len(_array)-1):
						line.append("N/A")
					else:
						line.append(_array[index])
				line = [str(val) for val in line]
				line_formatted = ", ".join(line)
				metadata.append(line_formatted)
				index += 1
			# return metadata

		if type(list_metadata[0]) == str:
			line = ", ".join(list_metadata)
			metadata.append(line)
			# return metadata

		if type(list_metadata[0]) == dict:

			# work with each dictionary key, one at a time
			for _key in list_metadata[0].keys():
				each_key_line = []
				metadata.append("# {}".format(_key))
				for _array in list_metadata:
					each_key_line.append(_array[_key])
				each_key_line = [str(val) for val in each_key_line]
				line_formatted = ", ".join(each_key_line)
				metadata.append(line_formatted)

	def makeup_output_file_name(self, nexus_file_name='', output_folder='./'):
		short_nexus_file_name = os.path.basename(nexus_file_name)
		base_name, ext = os.path.splitext(short_nexus_file_name)
		new_name = str(Path(output_folder) / "{}_extracted.txt".format(base_name))
		return new_name

	@staticmethod
	def create_output_file_name(output_folder='./', nbr_nexus=0):
		clean_output_folder = os.path.abspath(output_folder)
		short_file_name = "metadata_from_{}_nexus.txt".format(nbr_nexus)
		return str(Path(clean_output_folder) / short_file_name)

	@staticmethod
	def get_short_version_instrument(instrument):
		if 'CG2' in instrument:
			return 'CG2'
		else:
			return 'CG3'

	@staticmethod
	def get_entry_value(nexus_file_name=None, list_entry_path=None):
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

		result_dict = OrderedDict()
		with h5py.File(nexus_file_name, 'r') as nxs:

			for _entry_path in list_entry_path:

				id = "_".join(_entry_path)

				nxs_path = None
				try:
					nxs_path = nxs
					for _item in _entry_path:
						nxs_path = nxs_path.get(_item)

				except AttributeError:
					result_dict[id] = None

				# format output
				if nxs_path is None:
					result_dict[id] = nxs_path

				elif type(nxs_path) == h5py._hl.group.Group:
					result = {}
					for _key in nxs_path.keys():
						value = nxs_path.get(_key)
						if type(value) == h5py._hl.dataset.Dataset:
							result[_key] = np.squeeze(value[()])
						else:
							result[_key] = value

					result_dict[id] = result

				elif type(nxs_path) == h5py._hl.dataset.Dataset:
					formated_data = Extract.format_array(nxs_path[()])
					result_dict[id] = formated_data

		return result_dict

	@staticmethod
	def format_array(str_array):

		if type(str_array) == np.float64:
			return str_array

		if str_array[0] == '[':
			# it's supposed to be an array

			# remove '[' and ']'
			format1 = str_array[1:-1]
			# split by space
			format2 = format1.split(" ")
			# remove \n
			format3 = []
			for val in format2:
				try:
					new_val = np.float(val.strip())
				except ValueError:
					new_val = str(val.strip())
				format3.append(new_val)
			return format3

		else:
			# it's just a string
			return str_array




