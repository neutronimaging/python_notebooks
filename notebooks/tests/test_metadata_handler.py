import pytest
from pathlib import Path
from __code.metadata_handler import MetadataHandler
import glob


class TestMetadataHandler:

    def setup_method(self):
        data_path = Path(__file__).parent
        self.tiff_path = Path(data_path) / 'data' / 'images' / 'tiff'

    def test_empty_dict_returned_if_not_files(self):
        dict_returned = MetadataHandler.retrieve_metadata()
        assert dict_returned == {}

    def test_correct_full_dict_returned(self):
        list_files = glob.glob(str(self.tiff_path) + '/*.tif')
        first_file = list_files[0]
        dict_returned = MetadataHandler.retrieve_metadata(list_files=[first_file])

        # 1 file recorded
        assert len(dict_returned.keys()) == 1

        # nbr of metadata
        assert len(dict_returned[first_file].keys()) == 109

        # correct metadata retrieved
        assert dict_returned[first_file][65062] == 'MotAperture.RBV:220.000000'

    def test_correct_requested_metadata_dict_returned(self):
        list_key = [65062, 65063]
        list_files = glob.glob(str(self.tiff_path) + '/*.tif')
        dict_returned = MetadataHandler.retrieve_value_of_metadata_key(list_files=list_files,
                                                                       list_key=list_key)
        assert dict_returned[list_files[0]][65062] == 'MotAperture.RBV:220.000000'
        assert dict_returned[list_files[1]][65062] == 'MotAperture.RBV:220.000000'
