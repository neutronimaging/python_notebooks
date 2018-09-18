from ipywidgets.widgets import interact
from ipywidgets import widgets
from IPython.core.display import display, HTML
import os
import numpy as np
import ipywe.fileselector
from __code import utilities

from __code.file_handler import  ListMostDominantExtension


class FormatFileNameIndex(object):

	def __init__(self, working_dir=''):
		self.working_dir = working_dir

	def select_input_folder(self):
		self.input_folder_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select Input Folder',
                                                             	    type='directory',
                                                                    start_dir=self.working_dir,
                                                                    multiple=False)
		self.input_folder_ui.show()

	def calculate_most_dominant_files(self):
		self.o_list_dominant = ListMostDominantExtension(working_dir = self.input_folder_ui.selected)
		self.o_list_dominant.calculate()

	def get_most_dominant_files(self):
		_result = self.o_list_dominant.get_files_of_selected_ext()
		self.list_files = _result.list_files
		self.ext = _result.ext


class NamingSchemaDefinition(object):

	ext = ''
	list_files = []
	working_dir = ''

	def __init__(self, o_format=None):
		if o_format:
			self.list_files = o_format.list_files
			self.ext = o_format.ext
			self.working_dir = o_format.working_dir

		if self.list_files:
			_random_input_list = utilities.get_n_random_element(input_list=self.list_files,
																	n=10)
			self.random_input_list = [os.path.basename(_file) for _file in _random_input_list]

	def current_naming_schema(self):
		pre_index_separator = self.box2.children[1].value
		schema = "<none_relevant_part>" + pre_index_separator + '<digit>' + self.ext
	    
		return schema

	def new_naming_schema(self):
		prefix = self.box1.children[1].value
		post_index_separator = self.box5.children[1].value
		nbr_digits = self.box7.children[1].value

		schema = prefix + post_index_separator + nbr_digits * '#' + self.ext
	    
		return schema

	def pre_index_text_changed(self, sender):
		self.box4.children[1].value = self.current_naming_schema()
		self.demo_output_file_name()

	def post_text_changed(self, sender):
		self.box6.children[1].value = self.new_naming_schema()
		self.demo_output_file_name()

	def show(self):

		# current schema name

		self.box2 = widgets.HBox([widgets.Label("Pre. Index Separator",
		                                  layout=widgets.Layout(width='15%')),
		                    widgets.Text(value='__',
		                                layout=widgets.Layout(width='5%'))])

		self.box4 = widgets.HBox([widgets.Label("Current Name Schema: ",
		                                  layout=widgets.Layout(width='20%')),
		                    widgets.Label(self.current_naming_schema(),
		                                 layout=widgets.Layout(width='20%')),
		                    widgets.Dropdown(options=self.random_input_list,
		                    	value=self.random_input_list[0],
		                    	description='Random Input',
		                    	layout=widgets.Layout(width='40%'))

		                    ])

		self.box2.children[1].on_trait_change(self.pre_index_text_changed, 'value')
		before = widgets.VBox([self.box2, self.box4])

		# new naming schema
		box_text_width = '10%'
		self.box1 = widgets.HBox([widgets.Label("Prefix File Name",
		                                  layout=widgets.Layout(width='15%')),
		                    widgets.Text(value='image',
		                                layout=widgets.Layout(width='25%'))])

		self.box5 = widgets.HBox([widgets.Label("New Index Separator",
		                                  layout=widgets.Layout(width='15%')),
		                    widgets.Text(value='_',
		                                layout=widgets.Layout(width=box_text_width))])

		self.box7 = widgets.HBox([widgets.Label("Number of digits",
		                                  layout=widgets.Layout(width='15%')),
		                    widgets.IntText(value=4,
		                                   layout=widgets.Layout(width=box_text_width))])

		self.box8 = widgets.HBox([widgets.Label("Offset",
												layout=widgets.Layout(width='15%')),
								  widgets.IntText(value=0,
												  layout=widgets.Layout(width=box_text_width))])

		self.box6 = widgets.HBox([widgets.Label("New Name Schema: ",
		                                  layout=widgets.Layout(width='20%')),
		                    widgets.Label(self.new_naming_schema(),
		                                 layout=widgets.Layout(width='20%'))])

		self.box1.children[1].on_trait_change(self.post_text_changed, 'value')
		self.box5.children[1].on_trait_change(self.post_text_changed, 'value')
		self.box7.children[1].on_trait_change(self.post_text_changed, 'value')
		self.box8.children[1].on_trait_change(self.post_text_changed, 'value')

		after = widgets.VBox([self.box1, self.box5, self.box7, self.box8, self.box6])

		accordion = widgets.Accordion(children=[before, after])
		accordion.set_title(0, 'Current Schema Name')
		accordion.set_title(1, 'New Naming Schema')

		output_ui_1 = widgets.HBox([widgets.Label("Example of naming: ",
												layout=widgets.Layout(width='20%'))])

		self.output_ui_2 = widgets.HBox([widgets.Label("Old name: ",
		                                  layout=widgets.Layout(width='40%')),
		                    widgets.Label("",
		                                 layout=widgets.Layout(width='60%'))])

		self.output_ui_3 = widgets.HBox([widgets.Label("New name: ",
		                                  layout=widgets.Layout(width='40%')),
		                    widgets.Label("",
		                                 layout=widgets.Layout(width='60%'))])

		vbox = widgets.VBox([accordion, output_ui_1, self.output_ui_2, self.output_ui_3])
		display(vbox)

		self.demo_output_file_name()

	def demo_output_file_name(self):
		input_file = os.path.basename(self.list_files[0])
		self.output_ui_2.children[1].value = input_file

		old_index_separator = self.get_old_index_separator()
		new_prefix_name = self.get_new_prefix_name()
		new_index_separator = self.get_new_index_separator()
		new_number_of_digits = self.get_new_number_of_digits()
		offset = self.box8.children[1].value

		try:
			new_name = self.geneate_new_file_name(input_file,
												  old_index_separator,
												  new_prefix_name,
												  new_index_separator,
												  new_number_of_digits,
												  offset)
		except ValueError:
			new_name = 'ERROR while generating new file name!'

		self.output_ui_3.children[1].value = new_name

	def get_old_index_separator(self):
		return self.box2.children[1].value

	def get_new_prefix_name(self):
		return self.box1.children[1].value

	def get_new_index_separator(self):
		return self.box5.children[1].value

	def get_new_number_of_digits(self):
		return self.box7.children[1].value	

	def geneate_new_file_name(self, old_file_name, old_index_separator, new_prefix_name, new_index_separator,
							  new_number_of_digits, offset):
		[_pre_extension, _ext] = os.path.splitext(old_file_name)
		_name_separated = _pre_extension.split(old_index_separator)
		_index = np.int(_name_separated[-1]) + offset
		new_name = new_prefix_name + new_index_separator + \
				   '{:0{}}'.format(_index, new_number_of_digits) + \
				   self.ext
		return new_name

	def get_dict_old_new_filenames(self):
		list_of_input_files = self.list_files

		old_index_separator = self.get_old_index_separator()
		new_prefix_name = self.get_new_prefix_name()
		new_index_separator = self.get_new_index_separator()
		new_number_of_digits = self.get_new_number_of_digits()
		offset = self.box8.children[1].value

		list_of_input_basename_files = [os.path.basename(_file) for _file in list_of_input_files]

		new_list = {}
		for _file_index, _file in enumerate(list_of_input_basename_files):
			new_name = self.geneate_new_file_name(_file,
												  old_index_separator,
												  new_prefix_name,
												  new_index_separator,
												  new_number_of_digits,
												  offset)
			new_list[list_of_input_files[_file_index]] = new_name

		return new_list

	def select_export_folder(self):
		self.output_folder_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select Output Folder',
																	 start_dir=self.working_dir,
																	 multiple=False,
																	 next=self.export,
																	 type='directory')
		self.output_folder_ui.show()

	def export(self, value):
		dict_old_new_names = self.get_dict_old_new_filenames()
		new_output_folder = os.path.abspath(self.output_folder_ui.selected)

		utilities.copy_files(dict_old_new_names=dict_old_new_names,
							 new_output_folder=new_output_folder)

		self.new_list_files = dict_old_new_names