import glob
import os


def get_list_of_folders_with_specified_file_type(list_of_folders_to_check=None,
                                                 file_extension=['tiff', 'tif']):
    """
    check in the list of folder given (list_of_folders_to_check) if files of the type specified are there.
    If no file can be found in that folder with that type, the folder name is removed from the list

    :param:
      list_of_folders_to_check: example ['folder1', 'folder2', 'folder3'] list of full path to each folder
      file_extension: example ['tiff', 'tif'], ['fits'], ['.txt'] list of file extension to check for.
    :return:
      list of folders that do have at least one file with the correct file extension
    """
    if not (type(list_of_folders_to_check) is list):
        raise ValueError("list_of_folders_to_check must be a list!")

    if not (type(file_extension) is list):
        raise ValueError("file_extension must be a list!")

    list_of_folders_checked = []
    for _folder in list_of_folders_to_check:
        if not (os.path.exists(_folder)):
            break

        for _extension in file_extension:
            list_of_files = glob.glob(os.path.join(_folder, '*.{}'.format(_extension)))
            if len(list_of_files) > 0:
                list_of_folders_checked.append(_folder)
                break

    return list_of_folders_checked
