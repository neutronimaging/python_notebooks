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

# + run_control={"frozen": false, "read_only": false}
IPTS = 17685
# -

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/from_dsc_time_to_ascii_file_vs_time)
#
# <img src='__docs/__all/notebook_rules.png' />

# +
from __code.from_dsc_time_info_to_ascii_file_vs_time import CreateExportTimeStamp

from __code import system
system.System.select_working_dir()
from __code.__all import custom_style
custom_style.style()
# -

# # Select DSC Folder 

o_dsc = CreateExportTimeStamp(working_dir=system.System.get_working_dir())

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select TIFF Images Folder 
# -

o_dsc.select_tiff_folder()

# # Select Output Folder and Create Output File

o_dsc.select_output_folder_and_create_ascii_file()

# + run_control={"frozen": false, "read_only": false}

