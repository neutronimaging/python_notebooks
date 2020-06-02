import h5py
from pathlib import Path
from ipywidgets import widgets

from __code.file_folder_browser import FileFolderBrowser


class Extract(FileFolderBrowser):

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

		first_nexus_selected = list_nexus[0]

		dict_daslogs_keys = {}
		with h5py.File(first_nexus_selected, 'r') as nxs:
			for key in nxs['entry']['DASlogs'].keys():
				dict_daslogs_keys[key] = list(nxs['entry']['DASlogs'][key].keys())



