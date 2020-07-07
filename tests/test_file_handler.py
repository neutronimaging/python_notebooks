import pytest
from pathlib import Path
import numpy as np

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

	def test_retrieving_data(self):
		result = read_bragg_edge_fitting_ascii_format(full_file_name=self.ascii_file_name)
		pd_data = result['data']
		data_col3 = np.array(pd_data['3'])
		assert np.allclose(data_col3[0:4], [0.233055, 0.223026, 0.233431, 0.230279], atol=1e-5)

	def test_retrieving_xaxis(self):
		result = read_bragg_edge_fitting_ascii_format(full_file_name=self.ascii_file_name)
		pd_data = result['data']
		data_tof = np.array(pd_data['tof'])
		assert np.allclose(data_tof[0:4], [0.96, 11.2, 21.44, 31.68])
		data_lambda = np.array(pd_data['lambda'])
		assert np.allclose(data_lambda[0:4], [0.0197830, 0.01981425, 0.019845414, 0.01987658])
		data_index = np.array(pd_data['index'])
		assert np.all(data_index[0:4] == [0, 1, 2, 3])
