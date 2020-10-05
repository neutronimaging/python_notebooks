from ipywidgets import widgets
from IPython.core.display import display, HTML
import os
from PIL import Image
import collections

from __code import file_handler
from __code.file_folder_browser import FileFolderBrowser


class DisplayMetadata(FileFolderBrowser):

	def __init__(self, working_dir=''):
		super(DisplayMetadata, self).__init__(working_dir=working_dir)

	def display_metadata_list(self):

		self.list_images = self.list_images_ui.selected
		list_images = self.list_images

		image0 = list_images[0]
		o_image0 = Image.open(image0)

		info = collections.OrderedDict(sorted(o_image0.tag_v2.items()))
		display_format = []
		for tag, value in info.items():
			display_format.append("{} -> {}".format(tag, value))
		    
		self.box1 = widgets.HBox([widgets.Label("Select Metadata:",
		      	                            layout=widgets.Layout(width='10%')),
		        	            widgets.Dropdown(options=display_format,
		            	           value=display_format[0],
		                	                    layout=widgets.Layout(width='50%'))])
		display(self.box1)	

	def display_metadata_selected(self):

		metadata_selected = self.box1.children[1].value

		# retrieve key selected
		[key,value] = metadata_selected.split(' -> ')
		self.key = key

		# display file vs value of key selected
		display(widgets.Label("Metadata to display {}".format(metadata_selected)))
		export_txt = []
		for _file in self.list_images:
			o_image = Image.open(_file)
			o_dict = dict(o_image.tag_v2)
			_key = os.path.basename(_file)
			_value = o_dict[float(key)]
			export_txt.append("{} {}".format(_key, _value))
			box = widgets.HBox([widgets.Label("  {} -> ".format(_key),
		                                      layout=widgets.Layout(width='40%')),
		                        widgets.Label(" {}".format(_value),
		                                        layout=widgets.Layout(width='20%'))])
			display(box)

		self.export_txt = export_txt

	def export(self):

		output_folder = self.list_output_folders_ui.selected

		parent_folder = self.list_images[0].split(os.path.sep)[-2]
		metadata_name = 'metadata#{}'.format(self.key)
		output_file_name = os.path.join(output_folder, "{}_{}.txt".format(parent_folder, metadata_name))
		file_handler.make_ascii_file(metadata=['#Metadata: ' + self.key], 
									 data=self.export_txt,
									 dim='1d',
									 output_file_name=output_file_name)
