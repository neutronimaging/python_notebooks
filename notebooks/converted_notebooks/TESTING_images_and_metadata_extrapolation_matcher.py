# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.5.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
import os
import numpy as np
import pprint

import matplotlib.pyplot as plt
import time
import datetime

import pandas as pd
from __code import time_utility

from __code.images_and_metadata_extrapolation_matcher import ImagesAndMetadataExtrapolationMatcher
# -

# # Case 1 - file name information in both files

ascii1 = '/Volumes/my_book_thunderbolt_duo/IPTS/IPTS-20444-Regina/TESTING_SET/images_timestamp_infos.txt'
ascii2 = '/Volumes/my_book_thunderbolt_duo/IPTS/IPTS-20444-Regina/TESTING_SET/Sep_17_metadata_report_from_oncat.txt'

o_matcher = ImagesAndMetadataExtrapolationMatcher(ascii_file_1=ascii1, ascii_file_2=ascii2)

# +
# pprint.pprint("ascii1")
# pprint.pprint(o_matcher.ascii_file_1_dataframe)

# print("")

# pprint.pprint("ascii2")
# pprint.pprint(o_matcher.ascii_file_2_dataframe)
# -

pprint.pprint("Data merged")
pprint.pprint(o_matcher.get_merged_dataframe())

# # Case 2 - No filename information in one of the metadata

ascii1 = '/Volumes/my_book_thunderbolt_duo/IPTS/IPTS-20444-Regina/TESTING_SET/images_timestamp_infos.txt'
ascii3 = '/Volumes/my_book_thunderbolt_duo/IPTS/IPTS-20444-Regina/TESTING_SET/A49_3_at80C_4p1mm_120s_2_03_OCV_C03_2columns.txt'


o_matcher = ImagesAndMetadataExtrapolationMatcher(ascii_file_1=ascii1, ascii_file_2=ascii3)

# +
# print("ascii1")
# print(o_matcher.ascii_file_1_dataframe)

# +
# print("\nascii2")
# print(o_matcher.ascii_file_2_dataframe)

# +
ascii_file_1_dataframe = o_matcher.ascii_file_1_dataframe
ascii_file_1_dataframe.set_index('timestamp_user_format')

ascii_file_2_dataframe = o_matcher.ascii_file_2_dataframe
ascii_file_2_dataframe.set_index("timestamp_user_format");
# -

merged_dataframe = pd.merge(ascii_file_1_dataframe, ascii_file_2_dataframe, on="timestamp_user_format", how="outer")
merged_dataframe.sort_values(by='timestamp_user_format', inplace=True)
merged_dataframe = merged_dataframe.reset_index(drop=True)
merged_dataframe


# Ask which columns the user wants to extrapolate

list_columns = merged_dataframe.columns
list_columns


def get_first_metadata_and_index_value(index=-1, metadata_array=[], direction='left'):
    if direction == 'left':
        coeff = -1
    else:
        coeff = +1
        
    while (np.isnan(metadata_array[index])):
        index += coeff
        
        # if last file timestamp is > last metadata recorded, raise error
        if index >= len(metadata_array):
            raise ValueError("Not enough metadata to extrapolate value!")
        
    return [metadata_array[index], index]


import time
def convert_to_second(timestamp_value, timestamp_format="%Y-%m-%d %I:%M:%S"):
    d = datetime.datetime.strptime(timestamp_value, timestamp_format )
    return time.mktime(d.timetuple())    


# +
def calculate_extrapolated_metadata(global_index=-1, metadata_array=[], timestamp_array=[]):
    
#     print("calculate_extrapolated_metadata")
#     print("metadata_array: {}".format(metadata_array))
#     print("timestamp_array: {}".format(timestamp_array))
    
    [left_metadata_value, left_index] = get_first_metadata_and_index_value(index=global_index, 
                                                                           metadata_array=metadata_array,
                                                                           direction='left')
    [right_metadata_value, right_index] = get_first_metadata_and_index_value(index=global_index,
                                                                             metadata_array=metadata_array,
                                                                             direction='right')
    
#     print("-> left_metadata_value: {}".format(left_metadata_value))
#     print("-> left_index: {}".format(left_index))
#     print("-> right_metadata_value: {}".format(right_metadata_value))
#     print("-> right_index: {}".format(right_index))   
    
    left_timestamp_s_format = convert_to_second(timestamp_array[left_index])
    right_timestamp_s_format = convert_to_second(timestamp_array[right_index])
    
    x_timestamp_s_format = convert_to_second(timestamp_array[global_index])
    
    extra_value = extrapolate_value(x=x_timestamp_s_format,
                                   x_left=left_timestamp_s_format,
                                   x_right=right_timestamp_s_format,
                                   y_left=left_metadata_value,
                                   y_right=right_metadata_value)
    return extra_value
    


# +
def extrapolate_value(x=1, x_left=1, x_right=1, y_left=1, y_right=1):
    
#     print("in extrapolate_value")
#     print("--> x: {}".format(x))
#     print("--> x_left: {}".format(x_left))
#     print("--> x_right: {}".format(x_right))
#     print("--> y_left: {}".format(y_left))
#     print("--> y_right: {}".format(y_right))
    
    coeff = (float(y_right) - float(y_left)) / (float(x_right) - float(x_left))
#     print("---> coeff: {}".format(coeff))
    part1 = coeff * (float(x) - float(x_left))
#     print("--> part1: {}".format(part1))
#     print("--> part1 + float(y_left): {}".format(part1 + float(y_left)))
    return part1 + float(y_left)


# +
# let's pretend user selected 
columns_name_to_extrapolate = "Voltage"

metadata_array = merged_dataframe['Voltage']
timestamp_array = merged_dataframe['timestamp_user_format']

# pprint.pprint("metadata array")
# pprint.pprint(metadata_array)

new_metadata_array = []
voltage_extrapolated_array = []
for _index in np.arange(len(metadata_array)):
    
    _metadata_value = metadata_array[_index]
    if np.isnan(_metadata_value):
        _new_value = calculate_extrapolated_metadata(global_index=_index,
                                                    metadata_array=metadata_array,
                                                    timestamp_array=timestamp_array)
        voltage_extrapolated_array.append(_new_value)
    else:
        _new_value = _metadata_value
        
    new_metadata_array.append(_new_value)
   
# pprint.pprint("new metadata_array")
# pprint.pprint(new_metadata_array)
   
# -

time_column = timestamp_array
time_column_s = [convert_to_second(_time, timestamp_format="%Y-%m-%d %I:%M:%S") for _time in time_column]

# %matplotlib notebook

# +
# voltage (metadata file)
# -

timestamp_with_voltage_known = ascii_file_2_dataframe['timestamp_user_format']
time_column_voltage_known = timestamp_with_voltage_known
time_column_s_known = [convert_to_second(_time, timestamp_format="%Y-%m-%d %I:%M:%S") for _time in time_column_voltage_known]
voltage_column = ascii_file_2_dataframe['Voltage']

# +
# time stamp vs file name file
# -

list_index = list(np.where(np.isnan(merged_dataframe['Voltage'])))
time_column_voltage_unknown = np.array(timestamp_array)[list_index]

#time_column_voltage_unknown = ascii_file_1_dataframe['timestamp_user_format']
#time_column_voltage_unknown = time_column_voltage_unknown
time_column_s_unknown = [convert_to_second(_time, timestamp_format="%Y-%m-%d %I:%M:%S") for _time in time_column_voltage_unknown]


# +
fig, ax = plt.subplots()
ax.plot(time_column_s_known, voltage_column, '+', label='Time Stamp vs File Name')
ax.set_xlabel("Time (s)")
ax.set_ylabel("Voltage")

for _vl in time_column_s_unknown:
    ax.axvline(x=_vl, color='r', linestyle='--')

ax.plot(time_column_s_unknown, voltage_extrapolated_array, '*g', label='Extrapolated metadata')
#ax.axvline(x=time_column_s_unknown[0], color='r', linestyle='--', label="Regina's metadata")

ax.legend()
# -

















# Metadata from Regina's data set retrieve

# +
_dataframe3 = pd.read_csv(ascii3)
#_dataframe.set_index(INDEX)
_dataframe3

time_column = np.asarray(_dataframe3['time_user_format'])
data_column_ascii1 = np.asarray(_dataframe3['Voltage'])
#time_column
time_column_ascii1 = [get_seconds(_time) for _time in time_column]

# -

# Data coming from file_name vs time stamp

_dataframe1 = pd.read_csv(ascii1)
#_dataframe.set_index(INDEX)
_dataframe1

time_column = np.asarray(_dataframe1[' timestamp_user_format'])
time_column_s = [get_seconds(_time, time_format="%Y-%m-%d %I:%M:%S") for _time in time_column]

# +
fig, ax = plt.subplots()
ax.plot(time_column_ascii1, data_column_ascii1, '*-', label='Time Stamp vs File Name')
ax.set_xlabel("Time (s)")
ax.set_ylabel("Voltage")

for _vl in time_column_s[1:]:
    ax.axvline(x=_vl, color='r', linestyle='--')

ax.axvline(x=time_column_s[0], color='r', linestyle='--', label="Regina's metadata")

ax.legend()

# -

# Checking the conversion of time/date units

format1 = "2018-09-18 12:12:7"
format1_reader = "%Y-%m-%d %I:%M:%S"
format2 = "09/18/2018 12:10:35"
format2_reader = "%m/%d/%Y %I:%M:%S"

a="dfdfdf"
type(a) is list

# +
global_format = time.strptime(format1.strip(), format1_reader)

new_format = "{}/{}/{} {}:{}:{:}".format(global_format.tm_year,
                                        global_format.tm_mon,
                                        global_format.tm_mday,
                                        global_format.tm_hour,
                                        global_format.tm_min,
                                        global_format.tm_sec)
print("{} -> {}".format(format1, new_format))

# +
# global_format = time.strptime(format2.strip(), format2_reader)

# new_format = "{}/{}/{} {}:{}:{}".format(global_format.tm_year,
#                                         global_format.tm_mon,
#                                         global_format.tm_mday,
#                                         global_format.tm_hour,
#                                         global_format.tm_min,
#                                         global_format.tm_sec)
# print("{} -> {}".format(format2, new_format))
# -



_dataframe1


def format_time(old_format):
    global_format = time.strptime(old_format.strip(), format1_reader)
    new_format = "{}/{}/{} {}:{}:{:02d}".format(global_format.tm_year,
                                        global_format.tm_mon,
                                        global_format.tm_mday,
                                        global_format.tm_hour,
                                        global_format.tm_min,
                                        global_format.tm_sec)
    return new_format


data1_dt = _dataframe1[' timestamp_user_format']
data1_dt

_dataframe1

for _index, _date in enumerate(data1_dt):
    new_format = format_time(_date)
    data1_dt[_index] = new_format

data1_dt

if "##filename" in _dataframe:
    print("yes")

o_matcher = ImagesAndMetadataExtrapolationMatcher(filename_vs_timestamp=ascii1,
                                                  metadata_ascii_file=ascii2)

# output file

o_folder = SelectFolder(system=system, next_function=o_matcher.export_ascii)







import pandas as pd

pd_ascii1 = pd.read_csv(ascii1)
pd_ascii2 = pd.read_csv(ascii2)

pd_ascii1.set_index("#filename")

pd_ascii2.set_index("#filename")

merging_ascii = pd.merge(pd_ascii1, pd_ascii2, on='#filename', how='outer')
merging_ascii

timestamp1 = "2018-09-18 12:13:14"
timestamp2 = "2018/09/18 12:13:14"
timestamp3 = "18/09/2018 12:13:14"


o_time = time_utility.TimestampFormatter(timestamp=timestamp3)

o_time.format()

# # Select Metadata Info to Keep 

# + [markdown] run_control={"frozen": false, "read_only": false}
# **Allow users to define:**
#
#  * reference_line_showing_end_of_metadata
#  * start_of_data_after_how_many_lines_from_reference_line
#  * index or label of time info column in big table

# + run_control={"frozen": false, "read_only": false}
o_meta = MetadataFileParser(filename=o_file.metadata_file, 
                            meta_type='mpt',
                            time_label='time/s',
                            reference_line_showing_end_of_metadata='Number of loops',
                            end_of_metadata_after_how_many_lines_from_reference_line=1)
o_meta.parse()

o_meta.select_data_to_keep()
# -

# # Select Output Folder and Filename of new Formated Metadata File

o_meta.keep_only_columns_of_data_of_interest()
o_meta.select_output_location()

# # Where to go Next 

# Now, you probably want to run [this metadata_ascii_parser](./metadata_ascii_parser.ipynb) notebook in order to create a list of file names and their exact metadata values.


