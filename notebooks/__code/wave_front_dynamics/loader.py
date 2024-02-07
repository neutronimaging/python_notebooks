from IPython.core.display import HTML
from IPython.core.display import display
import pandas as pd
import re
import numpy as np

from __code._utilities.file import retrieve_metadata_value_from_ascii_file


def loading_linear_profile_file(file_name):

    result_dict = {}

    # retrieve the axis labels
    list_of_original_image_files = []
    nbr_files = 0
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
                matching_pattern = '\#\w*\s{1}\w*\s{1}\w*\s{1}\((\d*)'
                m = re.match(matching_pattern, line)
                nbr_files = int(m.group(1))
                this_line_contains_the_original_image_file_name = True

    axis_legend = [_line.strip() for _line in axis_legend]
    axis_legend = [_line.replace("#", "").strip() for _line in axis_legend]

    clean_list_of_original_image_file_name = []
    matching_pattern = '\#\s\*\s([/,\-,\w,\.]*)'

    # getting the list of raw images
    for _line in list_of_original_image_files:
        m = re.match(matching_pattern, _line)
        _clean_line = m.group(1)
        clean_list_of_original_image_file_name.append(_clean_line)

    result_dict['list_of_original_image_files'] = clean_list_of_original_image_file_name

    pd_object = pd.read_csv(file_name, comment='#',
                            names=axis_legend)

    list_of_pixel = np.array(pd_object[axis_legend[0]])

    pd_object = pd_object.set_index(axis_legend[0])
    names_of_columns = pd_object.columns
    list_of_data = []

    for _col_name in names_of_columns[1:]:
        _data = pd_object[[_col_name]]
        _data = _data.rename(columns={_col_name: "mean counts"})
        list_of_data.append(_data)

    result_dict['list_of_data'] = list_of_data

#    list_timestamp = np.arange(len(list_of_pixel))
    list_timestamp = np.arange(nbr_files)
    print(f"{list_of_pixel =}")
    print(f"{nbr_files =}")

    return {'list_of_data': list_of_data,
            'list_of_original_image_files': clean_list_of_original_image_file_name,
            'list_timestamp': list_timestamp,
            'list_of_ascii_files': clean_list_of_original_image_file_name}


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
                            names=['mean counts'],
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
