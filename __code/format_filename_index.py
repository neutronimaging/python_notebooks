from ipywidgets.widgets import interact
from ipywidgets import widgets
from IPython.core.display import display, HTML
import os
import numpy as np


class NamingSchemaDefinition(object):

	def __init__(self, ext='', random_input_list=[]):
		self.ext = ext
		self.random_input_list = random_input_list

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

	def post_text_changed(self, sender):
		self.box6.children[1].value = self.new_naming_schema()

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
		                    	description='Example Current Input',
		                    	layout=widgets.Layout(width='50%'))

		                    ])

		self.box2.children[1].on_trait_change(self.pre_index_text_changed, 'value')
		before = widgets.VBox([self.box2, self.box4])

		# new naming schema
		self.box1 = widgets.HBox([widgets.Label("Prefix File Name",
		                                  layout=widgets.Layout(width='15%')),
		                    widgets.Text(value='image',
		                                layout=widgets.Layout(width='25%'))])

		self.box5 = widgets.HBox([widgets.Label("New Index Separator",
		                                  layout=widgets.Layout(width='15%')),
		                    widgets.Text(value='_',
		                                layout=widgets.Layout(width='5%'))])

		self.box7 = widgets.HBox([widgets.Label("Number of digits",
		                                  layout=widgets.Layout(width='15%')),
		                    widgets.IntText(value=4,
		                                   layout=widgets.Layout(width='5%'))])

		self.box6 = widgets.HBox([widgets.Label("New Name Schema: ",
		                                  layout=widgets.Layout(width='20%')),
		                    widgets.Label(self.new_naming_schema(),
		                                 layout=widgets.Layout(width='20%'))])

		self.box1.children[1].on_trait_change(self.post_text_changed, 'value')
		self.box5.children[1].on_trait_change(self.post_text_changed, 'value')
		self.box7.children[1].on_trait_change(self.post_text_changed, 'value')

		after = widgets.VBox([self.box1, self.box5, self.box7, self.box6])




		accordion = widgets.Accordion(children=[before, after])
		accordion.set_title(0, 'Current Schema Name')
		accordion.set_title(1, 'New Naming Schema')
		display(accordion)

	def get_old_index_separator(self):
		return self.box2.children[1].value

	def get_new_prefix_name(self):
		return self.box1.children[1].value

	def get_new_index_separator(self):
		return self.box5.children[1].value

	def get_new_number_of_digits(self):
		return self.box7.children[1].value	

	def get_dict_old_new_filenames(self, list_of_input_files=[]):
		old_index_separator = self.get_old_index_separator()

		new_prefix_name = self.get_new_prefix_name()
		new_index_separator = self.get_new_index_separator()
		new_number_of_digits = self.get_new_number_of_digits()

		list_of_input_basename_files = [os.path.basename(_file) for _file in list_of_input_files]

		new_list = {}
		for _file_index, _file in enumerate(list_of_input_basename_files):
		    [_pre_extension, _ext] = os.path.splitext(_file)
		    _name_separated = _pre_extension.split(old_index_separator)
		    _index = np.int(_name_separated[-1])
		    new_name = new_prefix_name + new_index_separator + \
		    	'{:0{}}'.format(_index, new_number_of_digits) + \
		    	self.ext
		    new_list[list_of_input_files[_file_index]] = new_name

		return new_list

