import pytest
import os
from pathlib import Path
from __code import nexus_handler

class TestNexusHandler:

	def setup_method(self):
		data_path = os.path.dirname(__file__)
		self.nexus_file_name = os.path.abspath(Path(data_path) / 'data' / 'test.nxs.h5')

	def test_raise_error_with_no_input_file_name(self):
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
		nexus_file_name = 'tests/data/test.nxs.h5'

		result = nexus_handler.get_list_entries(nexus_file_name=self.nexus_file_name,
		                                        starting_entries=['entry','daslogs'])

		assert result['pv1'] == ['average_value',
		                         'maximum_value',
		                         'minimum_value',
		                         'value']
