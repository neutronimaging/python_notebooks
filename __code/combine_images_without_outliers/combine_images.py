import numpy as np
from ipywidgets import widgets
from IPython.core.display import display, HTML
from collections import OrderedDict
from pathlib import Path
import os

from __code.ipywe import fileselector
from __code.file_handler import retrieve_list_of_most_dominant_extension_from_folder
from __code._utilities.string import get_beginning_common_part_of_string_from_list
from __code import fileselector
from __code.file_folder_browser import FileFolderBrowser
from __code.file_handler import make_or_reset_folder


class CombineImagesAlgorithm:

	def __init__(self, list_array=None):
		if list_array is None:
			raise ValueError("Please provide a list of arrays!")

		# in future implementation, we may do something else when less than 3 arrays are provided
		if len(list_array) < 3:
			raise ValueError("Please provide at least 3 arrays!")

		self.check_arrays_have_same_size_and_dimensions(list_array=list_array)

	@staticmethod
	def check_arrays_have_same_size_and_dimensions(list_array=None):
		list_len_array = set([len(_array) for _array in list_array])
		if len(list_len_array) > 1:
			raise ValueError("Arrays do not have the same size!")

		# make sure all the dimensions have the same size
		list_shape_array = set([_array.shape for _array in list_array])
		if len(list_shape_array) > 1:
			raise ValueError("Arrays do not have the same dimension!")

	@staticmethod
	def mean_without_outliers(list_array=None):
		global_array = []
		for _array in list_array:
			global_array.append(_array)
		nbr_arrays = len(global_array)

		min_array = np.min(global_array, 0)
		max_array = np.max(global_array, 0)

		sum_array = np.sum(global_array, 0) - max_array - min_array
		mean_array = sum_array / (nbr_arrays - 2)

		return mean_array


class Interface:

	# after removing those characters from the end of file name, match same base file name
	nbr_character_to_remove = 0

	dict_new_name_old_base_name_match = {}
	# full_combine_dict = {'20200821_Femur_0010_000_000': {['20200821_Femur_0010_000_000_00000.tiff',
	#                                                       '20200821_Femur_0010_000_000_00001.tiff',
	#                                                       '20200821_Femur_0010_000_000_00002.tiff'],},
	#                      '20200821_Femur_0010_000_113': {['20200821_Femur_0010_000_113_00003.tiff',
	#                                                       '20200821_Femur_0010_000_113_00004.tiff',
	#                                                       '20200821_Femur_0010_000_113_00005.tiff']},
	#                      ...}
	full_combine_dict = OrderedDict()
	block_preview = True

	def __init__(self, working_dir="", debugging=False):
		self.working_dir = working_dir
		self.ipts_folder = self.working_dir
		if not debugging:
			self.select_data_folder_to_combine()

	def select_data_folder_to_combine(self):
		select_data = fileselector.FileSelectorPanel(instruction='Select folder of images to combine ...',
		                                                   start_dir=self.working_dir,
		                                                   next=self.preview_combine_result,
		                                                   type='directory',
		                                                   multiple=False)
		select_data.show()

	def preview_combine_result(self, data_folder):

		list_of_input_filenames = retrieve_list_of_most_dominant_extension_from_folder(folder=data_folder)[0]
		self.input_folder = str(Path(list_of_input_filenames[0]).parent)
		list_of_input_filenames = [os.path.basename(_file) for _file in list_of_input_filenames]
		self.list_of_input_filenames = list_of_input_filenames

		display(HTML('<span style="font-size: 20px; color:blue">SELECT ONLY the first images to '
		             'combine into 1 image! (Select at least 3 images)</span>'))

		verti_layout = widgets.VBox([widgets.SelectMultiple(options=list_of_input_filenames,
		                                                    layout=widgets.Layout(width="100%",
		                                                                          height="300px"))])
		display(verti_layout)
		input_selection_widget = verti_layout.children[0]
		input_selection_widget.observe(self.input_selection_changed, names='value')

		hori_layout = widgets.HBox([widgets.Label("Prefix of new filename will be ->",
		                                          layout=widgets.Layout(width='20%')),
		                            widgets.Label("Not Enough images selected to correctly combine!",
		                                          layout=widgets.Layout(width='80%'))])
		display(hori_layout)
		self.prefix_filename_widget = hori_layout.children[1]

		select_width = "400px"
		select_height = "300px"
		new_name_verti_layout = widgets.VBox([widgets.Label("New list of files"),
		                                      widgets.Select(options=[],
		                                                     layout=widgets.Layout(width="100%",
		                                                                           height=select_height))],
		                                     layout=widgets.Layout(width=select_width))
		new_name_verti_layout.children[1].observe(self.new_list_of_files_selection_changed, names='value')
		old_name_verti_layout = widgets.VBox([widgets.Label("Corresponding combined files"),
		                                      widgets.Select(options=[],
		                                                     layout=widgets.Layout(width="100%",
		                                                                           height=select_height))],
		                                     layout=widgets.Layout(width=select_width))

		hori_layout_2 = widgets.HBox([new_name_verti_layout,
		                              widgets.Label("  "),
		                              old_name_verti_layout],
		                             layout=widgets.Layout(width="900px"))
		display(hori_layout_2)
		self.hori_layout_2 = hori_layout_2
		hori_layout_2.layout.visibility = self.get_preview_visibility()
		self.final_list_of_files_combined_renamed_widget = new_name_verti_layout.children[1]
		self.corresponding_list_of_files_combined = old_name_verti_layout.children[1]

	def get_preview_visibility(self):
		if self.block_preview:
			return 'hidden'
		else:
			return 'visible'

	def input_selection_changed(self, value):
		list_of_files_selected = value['new']
		if len(list_of_files_selected) < 3:
			message = "Not Enough images selected to correctly combine!"
			self.block_preview = True
		else:
			message = get_beginning_common_part_of_string_from_list(list_of_text=list_of_files_selected)
			self.block_preview = False
		self.prefix_filename_widget.value = message
		self.hori_layout_2.layout.visibility = self.get_preview_visibility()

		len_string_before = len(list_of_files_selected[0])
		self.len_string_after = len(message)
		self.nbr_character_to_remove = len_string_before - self.len_string_after

		self.update_result_of_combination_summary()

	def update_result_of_combination_summary(self):
		if self.block_preview:
			return

		full_combine_dict = OrderedDict()
		list_of_input_filenames = self.list_of_input_filenames
		final_list_of_combined_images_renamed = []
		dict_new_name_old_base_name_match = {}

		_index = 0
		for _file in list_of_input_filenames:
			base_file_name = _file[:self.len_string_after]
			try:
				full_combine_dict[base_file_name].append(_file)
			except KeyError:
				full_combine_dict[base_file_name] = [_file]
				new_name = "{}_{:05d}".format(base_file_name, _index)
				dict_new_name_old_base_name_match[new_name] = base_file_name
				final_list_of_combined_images_renamed.append(new_name)
				_index += 1

		self.full_combine_dict = full_combine_dict
		self.final_list_of_files_combined_renamed_widget.options = final_list_of_combined_images_renamed
		self.dict_new_name_old_base_name_match = dict_new_name_old_base_name_match

	def new_list_of_files_selection_changed(self, value):
		new_selection = value['new']
		dict_new_name_old_base_name_match = self.dict_new_name_old_base_name_match
		if dict_new_name_old_base_name_match:
			base_name = dict_new_name_old_base_name_match[new_selection]
			corresponding_list_of_files = self.full_combine_dict[base_name]
			self.corresponding_list_of_files_combined.options = corresponding_list_of_files

	def select_output_folder(self):
		self.o_folder = FileFolderBrowser(working_dir=self.working_dir,
		                                  next_function=self.combine,
		                                  ipts_folder=self.ipts_folder)
		self.o_folder.select_output_folder_with_new(instruction="Select where to create the combine data folder ...")

		# o_folder = FileFolderBrowser(working_dir=self.working_dir,
		#                              next_function=self.combine)
		# o_folder.select_output_folder()

	def combine(self, output_folder):
		# remove shortcut buttons
		self.o_folder.list_output_folders_ui.shortcut_buttons.close()

		base_folder_name = os.path.basename(self.input_folder)
		new_folder = base_folder_name + "_combined"
		full_new_folder_name = os.path.join(os.path.abspath(output_folder), new_folder)
		make_or_reset_folder(full_new_folder_name)


