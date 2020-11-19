import pytest
from pathlib import Path

from __code._utilities import folder


class TestFolders:

    def setup_method(self):
        data_path = Path(__file__).parent.parent
        self.list_folders = [str(Path(data_path) / 'data' / 'images' / 'tiff'),
                             str(Path(data_path) / 'data' / 'images' / 'data_with_acquisition_cycle')]

    def test_list_of_folders_to_check_is_list(self):
        list_of_folders_to_check = "file_name"
        with pytest.raises(ValueError):
            folder.get_list_of_folders_with_specified_file_type(list_of_folders_to_check=list_of_folders_to_check)

    def test_file_extension_is_list(self):
        list_of_folders_to_check = ["folder1", "folder2"]
        file_extension = "file extension"
        with pytest.raises(ValueError):
            folder.get_list_of_folders_with_specified_file_type(list_of_folders_to_check=list_of_folders_to_check,
                                                                file_extension=file_extension)

    def test_folder_rejected_when_do_not_exist(self):
        list_of_folders_to_check = ['folder1', 'folder2']
        list_of_folders_checked = folder.get_list_of_folders_with_specified_file_type(
                list_of_folders_to_check=list_of_folders_to_check)
        assert len(list_of_folders_checked) == 0

    def test_correct_list_of_folders_found(self):
        list_of_folders_to_check = self.list_folders
        list_of_folders_checked = folder.get_list_of_folders_with_specified_file_type(
                list_of_folders_to_check=list_of_folders_to_check)
        assert list_of_folders_checked == list_of_folders_to_check
