
import glob
import os

from __code import file_handler


class CreateExportTimeStamp(object):

	def __init__(self, dsc_folder='', tiff_folder='', output_folder=''):
		self.dsc_folder = dsc_folder
		self.tiff_folder = tiff_folder
		self.output_folder = output_folder


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