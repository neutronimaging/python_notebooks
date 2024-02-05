from IPython.core.display import HTML
from IPython.core.display import display
import pandas as pd

from __code._utilities.file import retrieve_metadata_value_from_ascii_file


def loading_linear_profile_file(file_name):

    # retrieve the axis labels
    list_of_original_image_files = []
    this_line_contains_the_original_image_file_name = False
    with open(file_name, 'r') as f:
        for line in f.readlines():
            if line.startswith("##"):
                axis_legend = line[1:].split(',')

            if line.strip() == "#":
                this_line_contains_the_original_image_file_name = False

            if this_line_contains_the_original_image_file_name:
                list_of_original_image_files.append(line)

            if line.startswith("#List of files"):
                this_line_contains_the_original_image_file_name = True

    axis_legend = [_line.strip() for _line in axis_legend]
    axis_legend = [_line.replace("#", "").strip() for _line in axis_legend]


    print(f"{list_of_original_image_files =}")


    pd_object = pd.read_csv(file_name, comment='#', names=axis_legend)







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
