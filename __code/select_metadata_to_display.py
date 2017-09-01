from ipywidgets.widgets import interact
from ipywidgets import widgets
from IPython.core.display import display, HTML

from PIL import Image
from PIL.ExifTags import TAGS
import collections


class DisplayMetadata(object):

	def __init__(self, list_images=[]):
		self.list_images = list_images

	def display_metadata_list(self):
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

		# display file vs value of key selected
		display(widgets.Label("Metadata to display {}".format(metadata_selected)))
		export_txt = []
		for _file in list_images:
		    o_image = Image.open(_file)
		    o_dict = dict(o_image.tag_v2)
		    _key = os.path.basename(_file)
		    _value = o_dict[float(key)]
		    export_txt.append("{} {}".format(_key, _value))
		    box = widgets.HBox([widgets.Label("  {} -> ".format(_key),
		                                      layout=widgets.Layout(width='40%', height='10%')),
		                        widgets.Label(" {}".format(_value),
		                                        layout=widgets.Layout(width='20%', height='10%'))])
		    display(box)
