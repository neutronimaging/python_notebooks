import pytest
from pathlib import Path

from __code.file_handler import read_bragg_edge_fitting_ascii_format


class TestReadBraggEdgeFittingAsciiFormat:

	def setup_method(self):
		data_path = Path(__file__).parent
		self.ascii_file_name = Path(data_path) / 'data' / 'bragg_edge_fitting_all_regions.txt'

	def test_file_does_not_exist(self):
		ascii_file = 'does_not_exist'
		with pytest.raises(FileNotFoundError):
			read_bragg_edge_fitting_ascii_format(full_file_name=ascii_file)

	def test_retrieving_metadata_base_folder(self):
		result = read_bragg_edge_fitting_ascii_format(full_file_name=self.ascii_file_name)
		assert result['metadata']['base_folder'] == '/Users/j35/IPTS/VENUS/shared/testing_normalized'

	def test_retrieving_metadata_columns(self):
		result = read_bragg_edge_fitting_ascii_format(full_file_name=self.ascii_file_name)
		metadata_column = result['metadata']['columns']
		assert metadata_column['3'] == {'x0': '334', 'y0': '166', 'width': '17', 'height': '17'}
		assert len(metadata_column) == 9

	