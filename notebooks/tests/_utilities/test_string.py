import pytest

from __code._utilities import string


class TestGetBeginningCommonPartOfStringFromList:

    def test_no_argument_raises_error(self):
        with pytest.raises(ValueError):
            common_part_returned = string.get_beginning_common_part_of_string_from_list()

    def test_get_beginning_common_part_of_string_from_list(self):
        list_of_string = ['/Users/j35/IPTS/IPTS-24959/renamed_files/20202020_Femur_0010_000_000_00000.tiff',
                          '/Users/j35/IPTS/IPTS-24959/renamed_files/20202020_Femur_0010_000_000_00001.tiff',
                          '/Users/j35/IPTS/IPTS-24959/renamed_files/20202020_Femur_0010_000_000_00002.tiff',
                          '/Users/j35/IPTS/IPTS-24959/renamed_files/20202020_Femur_0010_000_000_00003.tiff']
        common_part_returned = string.get_beginning_common_part_of_string_from_list(list_of_text=list_of_string,
                                                                                    filename_spacer='_')
        common_part_expected = '/Users/j35/IPTS/IPTS-24959/renamed_files/20202020_Femur_0010_000_000'
        assert common_part_expected == common_part_returned

    def test_no_match(self):
        list_of_string = ['abc.txt', 'bce.txt', 'def.txt']
        common_part_returned = string.get_beginning_common_part_of_string_from_list(list_of_text=list_of_string,
                                                                                    filename_spacer='_')
        common_part_expected = ""
        assert common_part_expected == common_part_returned

    def test_get_beginning_common_part_of_string_from_list_case2(self):
        list_of_string = ['/Users/j35/IPTS/IPTS-24959/renamed_files/20202020_Femur_0010_000_000_00000.tiff',
                          '/Users/j35/IPTS/IPTS-24959/renamed_files/20202020_Femur_0010_000_000_00001.tiff',
                          '/Users/j35/IPTS/IPTS-24959/renamed_files/20202020_Femur_0010_000_000_00002.tiff',
                          '/Users/j35/IPTS/IPTS-24959/renamed_files/20202020_Femur_0010_000_110_00003.tiff']
        common_part_returned = string.get_beginning_common_part_of_string_from_list(list_of_text=list_of_string,
                                                                                    filename_spacer='_')
        common_part_expected = '/Users/j35/IPTS/IPTS-24959/renamed_files/20202020_Femur_0010_000'
        assert common_part_expected == common_part_returned
