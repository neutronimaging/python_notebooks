from pathlib import Path
import glob

from __code.group_images_by_cycle_for_panoramic_stitching.group_images_by_cycle import GroupImagesByCycle
from __code.group_images_by_cycle_for_panoramic_stitching.sort_images_within_each_cycle import SortImagesWithinEachCycle


class TestSortImagesWithinCycles:

    def setup_method(self):
        data_path = Path(__file__).parent.parent

        tiff_path = Path(data_path) / 'data' / 'images' / 'tiff'
        list_of_files = glob.glob(str(tiff_path) + '/*.tif')
        list_of_files.sort()
        self.list_of_files = list_of_files

        full_tiff_path = Path(data_path) / 'data' / 'images' / 'data_with_acquisition_cycle'
        full_list_of_files = glob.glob(str(full_tiff_path) + '/*.tif')
        full_list_of_files.sort()
        self.full_list_of_files = full_list_of_files

        self.list_of_metadata_key = [65045, 65041]

    def test_sort_dictionary(self):
        o_group = GroupImagesByCycle(list_of_files=self.full_list_of_files,
                                     list_of_metadata_key=self.list_of_metadata_key)
        o_group.run()

        dictionary_of_groups = o_group.dictionary_of_groups
        dictionary_of_filename_metadata = o_group.master_dictionary

        dict_how_to_sort = {'1st_variable': {'name': 'MotLiftTable',
                                             'is_ascending': True},
                            '2nd_variable': {'name': 'MotLongAxis',
                                             'is_ascending': True}}

        o_sort = SortImagesWithinEachCycle(dict_groups_filename=dictionary_of_groups,
                                           dict_filename_metadata=dictionary_of_filename_metadata)
        o_sort.sort(dict_how_to_sort=dict_how_to_sort)

        group0_sorted_calculated = o_sort.dict_groups_filename_sorted[0]
        raw_group0 = dictionary_of_groups[0]
        index_expected = [4, 5, 6, 3, 8, 7, 2, 1, 0]
        group0_sorted_expected = [raw_group0[_index] for _index in index_expected]

        for _calculated, _expected in zip(group0_sorted_calculated, group0_sorted_expected):
            assert _calculated == _expected
