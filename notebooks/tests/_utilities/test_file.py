import pytest
from pathlib import Path

from notebooks.__code._utilities import file


class TestFolders:

    def setup_method(self):
        data_path = Path(__file__).parent.parent
        self.ascii_file_name = str(Path(data_path) / 'data' / 'ascii' / 'bragg_edge_fitting_all_regions.txt')

    def test_retrieving_metadata(self):
        metadata_value_1 = "#base folder"
        value_returned_1 = file.retrieve_metadata_value_from_ascii_file(filename=self.ascii_file_name,
                                                                        metadata_name=metadata_value_1)
        value_expected = "/Users/j35/IPTS/VENUS/IPTS-25778_normalized"
        assert value_expected == value_returned_1

        metadata_value_2 = "base folder"
        value_returned_2 = file.retrieve_metadata_value_from_ascii_file(filename=self.ascii_file_name,
                                                                        metadata_name=metadata_value_2)
        assert value_expected == value_returned_2
