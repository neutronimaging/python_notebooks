import pytest
from pathlib import Path
from __code import nexus_handler


class TestGetListEntries:

	def setup_method(self):
		data_path = Path(__file__).parent
		self.nexus_file_name = Path(data_path) / 'data' / 'test.nxs.h5'

	def test_raise_error_if_no_input_file_name(self):
		"""no input file name"""
		nexus_file_name = None

		with pytest.raises(ValueError):
			_ = nexus_handler.get_list_entries(nexus_file_name=nexus_file_name)

	def test_raise_error_with_unknown_file_name(self):
		"""file does not exist"""
		nexus_file_name = "not_real_file_path"

		with pytest.raises(ValueError):
			_ = nexus_handler.get_list_entries(nexus_file_name=nexus_file_name)

	def test_raising_error_if_wrong_entry(self):
		"""make sure error is raised if entry is wrong"""
		with pytest.raises(KeyError):
			_ = nexus_handler.get_list_entries(nexus_file_name=self.nexus_file_name,
			                                   starting_entries=['entry_does_not_exist'])

	def test_data_retrieved(self):
		"""data correctly retrieved"""
		result = nexus_handler.get_list_entries(nexus_file_name=self.nexus_file_name,
		                                        starting_entries=['entry', 'daslogs'])

		assert result['pv1'] == ['average_value',
		                         'maximum_value',
		                         'minimum_value',
		                         'value']


class TestGetEntryValue:

	def setup_method(self):
		data_path = Path(__file__).parent
		self.nexus_file_name = Path(data_path) / 'data' / 'test.nxs.h5'

	def test_raise_error_if_no_input_file_name(self):
		with pytest.raises(ValueError):
			_ = nexus_handler.get_entry_value()

	def test_raise_error_if_file_do_not_exist(self):
		nexus_file_name = "not_real_file_path"

		with pytest.raises(ValueError):
			_ = nexus_handler.get_entry_value(nexus_file_name=nexus_file_name)

	def test_raising_attribute_error_if_wrong_entry(self):
		entry_path = ['wrong', 'path']
		with pytest.raises(AttributeError):
			_ = nexus_handler.get_entry_value(nexus_file_name=self.nexus_file_name,
			                                  entry_path=entry_path)

	def test_data_retrieved(self):
		entry_path = ['entry', 'daslogs', 'pv1', 'value']
		result = nexus_handler.get_entry_value(nexus_file_name=self.nexus_file_name,
		                                       entry_path=entry_path)
		assert result == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
