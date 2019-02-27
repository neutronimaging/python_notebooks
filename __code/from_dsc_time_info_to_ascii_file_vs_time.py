import glob
import os
from IPython.display import display
from IPython.core.display import HTML

from __code import file_handler
from __code.file_folder_browser import FileFolderBrowser


class CreateExportTimeStamp(FileFolderBrowser):

	def __init__(self, working_dir='./'):
		FileFolderBrowser.__init__(self, working_dir=working_dir)
		__slots__ = {'dsc_folder', 'tiff_folder', 'output_folder'}
		self.__select_input_folder()

	def __select_input_folder(self):
		self.next_function = self.output_select_dsc_folder
		self.select_input_folder(instruction='Select DSC folder ...')

	def output_select_dsc_folder(self, folder):
		self.dsc_folder = folder
		display(HTML('<span style="font-size: 20px; color:blue">You have selected the DSC folder: ' + folder +
					 '</span>'))
		parent_dsc_folder = os.path.dirname(self.dsc_folder)
		self.working_dir = parent_dsc_folder

	def select_tiff_folder(self):
		self.next_function = self.output_select_tiff_folder
		self.select_input_folder(instruction='Select TIFF folder ...')

	def output_select_tiff_folder(self, folder):
		self.tiff_folder = folder
		display(HTML('<span style="font-size: 20px; color:blue">You have selected the TIFF folder: ' + folder +
					 '</span>'))

	def select_output_folder_and_create_ascii_file(self):
		self.next_function = self.create_ascii_file
		self.select_output_folder(instruction='Select TIFF folder ...')

	def create_ascii_file(self, output_folder):
		self.output_folder = output_folder
		self.run()

	def run(self):
		# retrive metadata from dsc file
		folder = self.dsc_folder
		list_dsc_files = glob.glob(folder + '/*.dsc')
		dsc_metadata = file_handler.retrieve_metadata_from_dsc_list_files(list_files = list_dsc_files)

		# retrieve tiff files
		tiff_folder = self.tiff_folder
		list_tiff_files = glob.glob(tiff_folder + '/*.tif*')

		folder_name = os.path.basename(os.path.dirname(list_tiff_files[0]))
		ascii_file_name = os.path.join(os.path.abspath(self.output_folder), folder_name + '_timestamps.txt')

		list_keys = list(dsc_metadata.keys())
		list_keys.sort()

		# create list
		ascii_array = ["Filename, acquisition_time(os_format), acquisition_time(user_format), acquisition_duration(s)"]
		for _index, _key in enumerate(list_keys):
		    _line = "{}, {}, {}, {}".format(os.path.basename(list_tiff_files[_index]),
		                                   dsc_metadata[_key]['os_format'],
		                                   dsc_metadata[_key]['user_format'],
		                                   dsc_metadata[_key]['acquisition_time'])
		    ascii_array.append(_line)

		# export file
		file_handler.make_ascii_file(data=ascii_array, output_file_name=ascii_file_name, dim='1d')