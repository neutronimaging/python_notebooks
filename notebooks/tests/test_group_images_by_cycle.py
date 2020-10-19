from pathlib import Path
from __code.group_images_by_cycle_for_panoramic_stitching.group_images_by_cycle import GroupImagesByCycle
import glob


class TestMetadataHandler:

    def setup_method(self):
        data_path = Path(__file__).parent
        self.tiff_path = Path(data_path) / 'data' / 'images' / 'tiff'
        list_of_files = glob.glob(str(self.tiff_path) + '/*.tif')
        list_of_files.sort()
        self.list_of_files = list_of_files
        self.list_of_metadata_key = [65045, 65041]

    def test_create_master_dictionary(self):
        o_group = GroupImagesByCycle(list_of_files=self.list_of_files,
                                     list_of_metadata_key=self.list_of_metadata_key)
        o_group.create_master_dictionary()

        dict_expected = {'/Users/j35/git/python_notebooks/notebooks/tests/data/images/tiff/image001.tif': {
                                'MotLongAxis': '170.000000',
                                'MotLiftTable': '115.000000'},
                         '/Users/j35/git/python_notebooks/notebooks/tests/data/images/tiff/image002.tif': {
                                'MotLongAxis': '135.000000',
                                'MotLiftTable': '115.000000'},
                         '/Users/j35/git/python_notebooks/notebooks/tests/data/images/tiff/image003.tif': {
                                'MotLongAxis': '100.000000',
                                'MotLiftTable': '115.000000'},
                         '/Users/j35/git/python_notebooks/notebooks/tests/data/images/tiff/image004.tif': {
                                'MotLongAxis': '100.000000',
                                'MotLiftTable': '70.000000'},
                         '/Users/j35/git/python_notebooks/notebooks/tests/data/images/tiff/image005.tif': {
                                'MotLongAxis': '100.000000',
                                'MotLiftTable': '30.000000'},
                         '/Users/j35/git/python_notebooks/notebooks/tests/data/images/tiff/image006.tif': {
                                'MotLongAxis': '135.000000',
                                'MotLiftTable': '30.000000'},
                         '/Users/j35/git/python_notebooks/notebooks/tests/data/images/tiff/image007.tif': {
                                'MotLongAxis': '170.000000',
                                'MotLiftTable': '30.000000'},
                         '/Users/j35/git/python_notebooks/notebooks/tests/data/images/tiff/image008.tif': {
                                'MotLongAxis': '170.000000',
                                'MotLiftTable': '70.000000'},
                         '/Users/j35/git/python_notebooks/notebooks/tests/data/images/tiff/image009.tif': {
                                'MotLongAxis': '135.000000',
                                'MotLiftTable': '70.000000'},
                         }

        dict_returned = o_group.master_dictionary

        for _file in dict_expected.keys():
            _expected = dict_expected[_file]
            _returned = dict_returned[_file]
            for _key in _expected.keys():
                assert _expected[_key] == _returned[_key]
