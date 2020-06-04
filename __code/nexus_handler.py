from pathlib import Path
import h5py


def get_list_entries(nexus_file_name=None, starting_entries=None):
	'''

	:param nexus_file_name: hdf5 full file path
	:param starting_entries: list of entries
		example: starting_entries = ['entry','DASlogs']
	:return: dictionary showing the structure of the hdf5 from the starting_entries level
	    example: {'PV1': ['value', 'maximum_value', 'minimum_value', 'mean'],
	              'PV2': ['value', 'maximum_value', 'minimum_value', 'mean']}
	'''
	if nexus_file_name is None:
		raise ValueError("Please provide a full path to a nexus file name!")

	if not Path(nexus_file_name).exists():
		raise ValueError("File do not exist!")

	dict_daslogs_keys = {}
	with h5py.File(nexus_file_name, 'r') as nxs:

		nxs_path = nxs
		for _item in starting_entries:
			nxs_path = nxs_path.get(_item)

		if nxs_path is None:
			raise KeyError("entries not found!")

		for key in nxs_path.keys():
			dict_daslogs_keys[key] = list(nxs_path.get(key).keys())

	return dict_daslogs_keys


def get_entry_value(nexus_file_name=None, entry_path=None):
	'''

	:param nexus_file_name: hdf5 full file path
	:param entry_path: full path through the file to retrieve the information
		example: ['entry', 'DASlogs', 'PV1', 'value']
	:return: value at the given path in the hdf5 file
	'''
	if nexus_file_name is None:
		raise ValueError("Please provide a full path to a nexus file name!")

	if not Path(nexus_file_name).exists():
		raise ValueError("File do not exist!")

	with h5py.File(nexus_file_name, 'r') as nxs:

		try:
			nxs_path = nxs
			for _item in entry_path:
				nxs_path = nxs_path.get(_item)
		except AttributeError:
			raise AttributeError("Path specify in the HDF5 is wrong!")

		return list(nxs_path)
