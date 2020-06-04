import copy
import h5py
from pathlib import Path
from ipywidgets import widgets
from IPython.core.display import display
from __code.nexus_handler import get_list_entries, get_entry_value
from __code.file_folder_browser import FileFolderBrowser
from __code.time_utility import AbsoluteTimeHandler

STARTING_ENTRIES = ['entry', 'DASlogs']

class Extract(FileFolderBrowser):

	first_nexus_selected = ''
	widget_height = "400px"

	def __init__(self, working_dir=''):
		super(Extract, self).__init__(working_dir=working_dir)

	def select_nexus(self):
		o_file = FileFolderBrowser(working_dir=self.working_dir,
		                           next_function=self.select_metadata)
		o_file.select_images(instruction="Select the NeXus files to extract infos from!",
		                     multiple_flag=True,
		                     filters={"NeXus": '*.nxs.h5'})

	def select_metadata(self, list_nexus=None):
		if list_nexus is None:
			return

		self.first_nexus_selected = list_nexus[0]
		self.dict_daslogs_keys = get_list_entries(nexus_file_name=self.first_nexus_selected,
		                             starting_entries=STARTING_ENTRIES)

		self.display_widgets()

	def display_widgets(self):

		dict_daslogs_keys = self.dict_daslogs_keys
		nexus_path = self.first_nexus_selected

		self.list_daslogs_keys = list(dict_daslogs_keys.keys())
		first_daslogs_key = self.list_daslogs_keys[0]
		list_keys_of_first_daslogs_key = list(dict_daslogs_keys[first_daslogs_key])
		first_key = list_keys_of_first_daslogs_key[0]
		value_of_first_selected_element = None
		with h5py.File(nexus_path, 'r') as nxs:
			value_of_first_selected_element = (list(nxs['entry']['DASlogs'][first_daslogs_key][first_key]))

		search_box = widgets.HBox([widgets.Label("Search:"),
		                           widgets.Text("",
		                                        layout=widgets.Layout(width="30%"))])
		search_text_widget = search_box.children[1]
		search_text_widget.observe(self.search_text_changed, names='value')

		key_layout = widgets.VBox([widgets.Label("X-axis"),
		                           widgets.Select(options=list_keys_of_first_daslogs_key),
		                           widgets.Label("Y-axis"),
		                           widgets.Select(options=list_keys_of_first_daslogs_key),
		                           ])
		value_layout = widgets.VBox([widgets.Label("Value"),
		                             widgets.Select(options=value_of_first_selected_element),
		                             widgets.Label("Value"),
		                             widgets.Select(options=value_of_first_selected_element)],
		                            )

		hori_box = widgets.HBox([widgets.Select(options=self.list_daslogs_keys,
		                                        value=first_daslogs_key,
		                                        layout=widgets.Layout(width="400px",
		                                                              height=self.widget_height)),
		                         key_layout,
		                         value_layout],
		                        layout=widgets.Layout())

		display(search_box)
		display(hori_box)

		self.top_keys_widgets = hori_box.children[0]

		self.x_axis_intermediate_key_widget = key_layout.children[1]
		self.y_axis_intermediate_key_widget = key_layout.children[3]

		self.x_axis_intermediate_value_widget = value_layout.children[1]
		self.y_axis_intermediate_value_widget = value_layout.children[3]

		self.top_keys_widgets.observe(self.top_keys_changed, names='value')
		self.x_axis_intermediate_key_widget.observe(self.x_axis_intermediate_value_changed, names='value')
		self.y_axis_intermediate_key_widget.observe(self.y_axis_intermediate_value_changed, names='value')

		self.top_keys_widget_value = self.top_keys_widgets.value

	def top_keys_changed(self, value):
		new_top_key = value['new']
		self.top_keys_widget_value = new_top_key
		list_intermediate_keys = list(self.dict_daslogs_keys[new_top_key])
		self.x_axis_intermediate_key_widget.options = list_intermediate_keys
		self.x_axis_intermediate_key_widget.value = list_intermediate_keys[0]
		self.y_axis_intermediate_key_widget.options = list_intermediate_keys
		self.y_axis_intermediate_key_widget.value = list_intermediate_keys[0]

	def x_axis_intermediate_value_changed(self, value=None):
		new_intermediate_key = value['new']
		first_daslogs_key =self.top_keys_widget_value
		with h5py.File(self.first_nexus_selected, 'r') as nxs:
			value_of_first_selected_element = (list(nxs['entry']['DASlogs'][first_daslogs_key][new_intermediate_key]))
		self.x_axis_intermediate_value_widget.options = value_of_first_selected_element

	def y_axis_intermediate_value_changed(self, value=None):
		new_intermediate_key = value['new']
		# value_of_first_selected_element = None
		first_daslogs_key = self.top_keys_widget_value
		with h5py.File(self.first_nexus_selected, 'r') as nxs:
			value_of_first_selected_element = (list(nxs['entry']['DASlogs'][first_daslogs_key][new_intermediate_key]))
		self.y_axis_intermediate_value_widget.options = value_of_first_selected_element

	def search_text_changed(self, value):
		new_text = value['new']
		if new_text == "":
			self.top_keys_widgets.value = self.list_daslogs_keys[0]
			return

		for key in self.list_daslogs_keys:
			if new_text in key:
				self.top_keys_widgets.value = key
				return

	def extract(self, top_key_widget_value=None, x_axis_key=None, y_axis_key=None):

		top_key_widget_value = top_key_widget_value if top_key_widget_value else self.top_keys_widget_value
		x_axis_key = x_axis_key if x_axis_key else self.x_axis_intermediate_key_widget.value
		y_axis_key = y_axis_key if y_axis_key else self.y_axis_intermediate_key_widget.value

		if (x_axis_key == 'time') or (y_axis_key == 'time'):
			use_absolute_time_offset = True

		top_entry_path = STARTING_ENTRIES
		top_entry_path.append(top_key_widget_value)

		x_axis_entry_path = copy.deepcopy(top_entry_path)
		x_axis_entry_path.append(x_axis_key)
		x_axis_array = get_entry_value(nexus_file_name=self.first_nexus_selected,
		                               entry_path=x_axis_entry_path)
		y_axis_entry_path = copy.deepcopy(top_entry_path)
		y_axis_entry_path.append(y_axis_key)
		y_axis_array = get_entry_value(nexus_file_name=self.first_nexus_selected,
		                               entry_path=y_axis_entry_path)

		if use_absolute_time_offset:
			starting_time = get_entry_value(nexus_file_name=self.first_nexus_selected,
		                                    entry_path=['entry','start_time'])
			if x_axis_key == 'time':
				time_axis = x_axis_array
			else:
				time_axis = y_axis_array

			o_absolute = AbsoluteTimeHandler(initial_absolute_time=starting_time[0])

			absolute_time_axis = o_absolute.get_absolute_time_for_this_delta_time_array(delta_time_array=time_axis)

	