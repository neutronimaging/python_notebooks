from IPython.core.display import HTML
from IPython.core.display import display
import pandas as pd

from __code._utilities.file import retrieve_metadata_value_from_ascii_file


def loading_linear_profile_file(list_of_ascii_files):
    display(HTML("Loading using linear method ... "))







    pass


def loading_radial_profile_file(list_of_ascii_files):
    display(HTML("Loading using radial method ... "))

    list_of_ascii_files.sort()

    list_of_data = []
    list_of_original_image_files = []
    list_of_timestamp = []
    for _file in list_of_ascii_files:
        _data = pd.read_csv(_file,
                            skiprows=6,
                            delimiter=",",
                            names=['pixel', 'mean counts'],
                            dtype=float,
                            index_col=0)
        list_of_data.append(_data)
        _original_image_file = retrieve_metadata_value_from_ascii_file(filename=_file,
                                                                       metadata_name="# source image")
        list_of_original_image_files.append(_original_image_file)
        _time_stamp = retrieve_metadata_value_from_ascii_file(filename=_file,
                                                              metadata_name="# timestamp")
        list_of_timestamp.append(_time_stamp)

    nbr_files = str(len(list_of_ascii_files))
    display(HTML('<span style="font-size: 20px; color:blue">Notebooks successfully loaded the ' + nbr_files +
                 ' ASCII profile files!</span>'))

    return {'list_of_ascii_files':list_of_ascii_files,
            'list_timestamp': list_of_timestamp,
            'list_of_data': list_of_data,
            'list_of_original_image_files': list_of_original_image_files}
