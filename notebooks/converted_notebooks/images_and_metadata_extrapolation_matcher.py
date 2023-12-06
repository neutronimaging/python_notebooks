# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.15.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/tutorials/imaging-notebooks/images-and-metadata-extrapolation-matcher/)
#
# <img src='__docs/__all/notebook_rules.png' />

# # Select your IPTS

from __code.select_files_and_folders import SelectAsciiFile, SelectFolder
from __code.images_and_metadata_extrapolation_matcher import ImagesAndMetadataExtrapolationMatcher
# %matplotlib notebook
from __code import system
system.System.select_working_dir(notebook='images_and_metadata_extrapolation_matcher')
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select the File Name vs Time Stamp text File
# -

# This file created by running [create_list_of_file_name_vs_time_stamp](create_list_of_file_name_vs_time_stamp.ipynb) notebook!

o_select_ascii1 = SelectAsciiFile(system=system)

# # Select Metadata vs Time Stamp text File 

# File creatd by either
#
# - [metadata_ascii_parser](metadata_ascii_parser.ipynb)
#
# **or/and**
#
# - [list_metadata_and_time_with_oncat](list_metadata_and_time_with_oncat.ipynb)

o_select_ascii2 = SelectAsciiFile(system=system)

# # Select Data to Merge

o_matcher = ImagesAndMetadataExtrapolationMatcher(ascii_file_1=o_select_ascii1.ascii_file,
                                                  ascii_file_2=o_select_ascii2.ascii_file)

# # Extrapolate and Display Results

o_matcher.extrapolate_selected_metadata()

# # Select Output Folder 

o_folder = SelectFolder(system=system, next_function=o_matcher.export_ascii)


