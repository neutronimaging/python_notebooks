import glob
import os

from ipywidgets.widgets import interact
from ipywidgets import widgets
from IPython.core.display import display, HTML


class MergeFolders(object):

	def __init__(self, list_folders=[]):
		self.list_folders = list_folders

	def check_number_of_files(self):
		# initialization of dictionary that will store the list of files
		list_files_dict = {}
		list_folders = self.list_folders

		nbr_files = {}
		for _folder in list_folders:
		    _list_files = glob.glob(_folder + "/*.*")
		    _short = os.path.basename(_folder)
		    list_files_dict[_short] = _list_files
		    nbr_files[_short] = len(_list_files)

		# checking the folders have the same number of files
		values = set(nbr_files.values())
		if len(values) > 1:
		    raise ValueError("Folder do not have the same number of files!")

		self.list_files_dict = list_files_dict

	def how_many_folders(self):
		nbr_folder = len(self.list_folders)
		radio_list_string = [str(_index) for _index in np.arange(2, nbr_folder+1)]
		self.bin_size = widgets.RadioButtons(options=radio_list_string,
		                               value=radio_list_string[0])
		display(self.bin_size)


	def how_to_combine(self):
		self.combine_method = widgets.RadioButtons(options=['add','mean'],
		                                             value='add')
		display(self.combine_method)

	def load_list_files(self, filename_array=[]):
	    data = []
	    for _filename in filename_array:
	        _data = file_handler.load_data(filename=_filename)
	        data.append(_data)
	    return data

	def add(self, array=[]):
	    return np.array(array).sum(axis=0)

	def mean(self, array=[]):
	    return np.array(array).mean(axis=0)

	def run(self):
		merged_images = {'file_name': [],
                'data': []}
		nbr_files = list(values)[0]

		box1 = widgets.HBox([widgets.Label("Merging Progress:",
		                                      layout=widgets.Layout(width='10%')),
		                        widgets.IntProgress(max=nbr_files)])
		display(box1)
		w1 = box1.children[1]

		for _index_file in np.arange(nbr_files):
		    _list_file_to_merge = []
		    for _key in list_files_dict.keys():
		        _file = list_files_dict[_key][_index_file]
		        _list_file_to_merge.append(_file)
		        merged_images['file_name'].append(os.path.basename(_file))
		    
		    _data_array = load_list_files(_list_file_to_merge)
		    merged_data = add(_data_array)
		    
		    w1.value = _index_file + 1
    
    
