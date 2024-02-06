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

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/tutorials/imaging-notebooks/list-metadata-and-time-with-oncat/)
#
# <img src='__docs/__all/notebook_rules.png' />

# # Select Your IPTS 

# +
from __code.select_files_and_folders import SelectFiles, SelectFolder
from __code.list_metadata_and_time_with_oncat import ListMetadata

from __code import system
system.System.select_working_dir(notebook='list_metadata_and_time_with_oncat')
from __code.__all import custom_style
custom_style.style()
# -

# # Select Images 

o_select = SelectFiles(system=system)

# # Log in to ONCat 

o_list = ListMetadata()

# # Select Metadata to Keep 

o_list.select_metadata(system=system, list_of_files=o_select.list_of_files)

# # Create and Export ASCII File

o_output_folder = SelectFolder(system=system, next_function=o_list.export_ascii)


