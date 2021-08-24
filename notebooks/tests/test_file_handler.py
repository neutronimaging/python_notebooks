import pytest
from pathlib import Path
import numpy as np

from notebooks.__code.file_handler import read_bragg_edge_fitting_ascii_format


class TestReadBraggEdgeFittingAsciiFormat:

    def setup_method(self):
        data_path = Path(__file__).parent
        self.ascii_file_name = Path(data_path) / 'data' / 'ascii' / 'bragg_edge_fitting_all_regions.txt'

    def test_file_does_not_exist(self):
        ascii_file = 'does_not_exist'
        with pytest.raises(FileNotFoundError):
            read_bragg_edge_fitting_ascii_format(full_file_name=ascii_file)

    def test_retrieving_metadata_columns(self):

        print(f"self.ascii_file_name: {self.ascii_file_name}")
        print(f"data_path = Path(__file__).parent: {Path(__file__).parent}")
        data_path = Path(__file__).parent
        import glob
        print(f"glob(data_path): {glob.glob(str(data_path) + '/data/*')}")
        my_data_path = "/home/runner/work/python_notebooks/notebooks/tests/data/"
        print(f"glob(my_data_path): {glob.glob(my_data_path)}")
        print("in master")

        result = read_bragg_edge_fitting_ascii_format(full_file_name=self.ascii_file_name)
        metadata_column = result['metadata']['columns']

        assert metadata_column['3'] == {'x0'                                                                : '285',
                                        'y0'                                                                : '131',
                                        'width'                                                             : '171',
                                        'height'                                                            : '171',
                                        'kropff'                                                            : {
                                            'a0'          : '0.05697761445846593', 'b0': '-12.17789476349729',
                                            'a0_error'    : '0.012625967415442281', 'b0_error': '0.32166122161751043',
                                            'ahkl'        : '0.22249188576171708', 'bhkl': '-7.201720779647523',
                                            'ahkl_error'  : '0.01749711471030342', 'bhkl_error': '0.49197822510433087',
                                            'ldahkl'      : '0.0368126543734365', 'tau': '0.00018227258697928991',
                                            'sigma'       : '0.00027024177029020614',
                                            'ldahkl_error': '0.00033445772089875196',
                                            'tau_error'   : '0.00012216476414800265',
                                            'sigma_error' : '0.0001071763960918388'}, 'march_dollase'       : {
                'd_spacing': 'None', 'sigma': 'None', 'alpha': 'None', 'a1': 'None', 'a2': 'None', 'a5': 'None',
                'a6'       : 'None', 'd_spacing_error': 'None', 'sigma_error': 'None', 'alpha_error': 'None',
                'a1_error' : 'None', 'a2_error': 'None', 'a5_error': 'None', 'a6_error': 'None'}}
        assert len(metadata_column) == 86
        # assert False

    def test_retrieving_data(self):
        result = read_bragg_edge_fitting_ascii_format(full_file_name=self.ascii_file_name)
        pd_data = result['data']
        data_col3 = np.array(pd_data['3'])
        print(data_col3[0:4])
        assert np.allclose(data_col3[0:4], [0.00078657, 0.00066687, 0.00100886, 0.00068397], atol=1e-5)

    def test_retrieving_xaxis(self):
        result = read_bragg_edge_fitting_ascii_format(full_file_name=self.ascii_file_name)
        pd_data = result['data']
        data_tof = np.array(pd_data['tof'])
        assert np.allclose(data_tof[0:4], [0.96, 11.2, 21.44, 31.68])
        data_lambda = np.array(pd_data['lambda'])
        assert np.allclose(data_lambda[0:4], [0.0197830, 0.01981425, 0.019845414, 0.01987658])
        data_index = np.array(pd_data['index'])
        assert np.all(data_index[0:4] == [0, 1, 2, 3])
