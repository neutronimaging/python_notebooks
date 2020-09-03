import numpy as np
from ipywidgets import widgets
from IPython.core.display import display, HTML

from __code.ipywe import fileselector
from __code.file_handler import retrieve_list_of_most_dominant_extension_from_folder
from __code._utilities.string import get_beginning_common_part_of_string_from_list


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

	def __init__(self, working_dir="", debugging=False):
		self.working_dir = working_dir
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

		display(HTML('<span style="font-size: 20px; color:blue">SELECT ONLY the first images to '
		             'combine into 1 image! (Select at least 3 images)</span>'))

		verti_layout = widgets.VBox([widgets.SelectMultiple(options=list_of_input_filenames,
		                                                    layout=widgets.Layout(width="100%",
		                                                                          height="300px"))])
		display(verti_layout)
		input_selection_widget = verti_layout.children[0]
		input_selection_widget.observe(self.input_selection_changed, names='value')

		hori_layout = widgets.HBox([widgets.Label("Prefix new filename will be ->",
		                                          layout=widgets.Layout(width='15%')),
		                            widgets.Label("Not Enough images selected to correctly combine!",
		                                          layout=widgets.Layout(width='80%'))])
		display(hori_layout)
		self.prefix_filename_widget = hori_layout.children[1]

		new_name_verti_layout = widgets.VBox([widgets.Label("New list of files"),
		                                      widgets.Select(options=[],
		                                                     layout=widgets.Layout(width="100%%",
		                                                                           height="300px"))],
		                                     layout=widgets.Layout(width='300px'))
		old_name_verti_layout = widgets.VBox([widgets.Label("Combined files"),
		                                      widgets.Select(options=[],
		                                                     layout=widgets.Layout(width="100%",
		                                                                           height="300px"))],
		                                     layout=widgets.Layout(width='300px'))

		hori_layout_2 = widgets.HBox([new_name_verti_layout,
		                              widgets.Label("  "),
		                              old_name_verti_layout])
		display(hori_layout_2)





	def input_selection_changed(self, value):
		list_of_files_selected = value['new']
		if len(list_of_files_selected) < 3:
			message = "Not Enough images selected to correctly combine!"
		else:
			message = get_beginning_common_part_of_string_from_list(list_of_text=list_of_files_selected)
		self.prefix_filename_widget.value = message




