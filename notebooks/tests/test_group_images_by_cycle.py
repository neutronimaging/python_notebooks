from pathlib import Path
from __code.group_images_by_cycle_for_panoramic_stitching.group_images_by_cycle import GroupImagesByCycle
import glob


class TestMetadataHandler:

    def setup_method(self):
        data_path = Path(__file__).parent

        tiff_path = Path(data_path) / 'data' / 'images' / 'tiff'
        list_of_files = glob.glob(str(tiff_path) + '/*.tif')
        list_of_files.sort()
        self.list_of_files = list_of_files

        full_tiff_path = Path(data_path) / 'data' / 'images' / 'data_with_acquisition_cycle'
        full_list_of_files = glob.glob(str(full_tiff_path) + '/*.tif')
        full_list_of_files.sort()
        self.full_list_of_files = full_list_of_files

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

    def test_group_dictionary(self):
        o_group = GroupImagesByCycle(list_of_files=self.full_list_of_files,
                                     list_of_metadata_key=self.list_of_metadata_key)
        o_group.create_master_dictionary()
        o_group.group()

        assert len(o_group.dictionary_of_groups.keys()) == 3

        expected_list_group0 = self.full_list_of_files[:9]
        assert len(o_group.dictionary_of_groups[0]) == len(expected_list_group0)

        for _file_returned, _file_expected in zip(o_group.dictionary_of_groups[0], expected_list_group0):
            assert _file_expected == _file_returned

        expected_list_group1 = self.full_list_of_files[9:18]
        assert len(o_group.dictionary_of_groups[1]) == len(expected_list_group1)

        for _file_returned, _file_expected in zip(o_group.dictionary_of_groups[1], expected_list_group1):
            assert _file_expected == _file_returned
