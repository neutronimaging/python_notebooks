# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# + [markdown] run_control={"frozen": false, "read_only": false}
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/create_list_of_file_name_vs_time_stamp)

# + [markdown] run_control={"frozen": false, "read_only": false}
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code.create_list_of_file_name_vs_time_stamp import CreateListFileName

from __code import system
system.System.select_working_dir()
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Image Folder 

# + run_control={"frozen": false, "read_only": false}
o_file_time_stamp = CreateListFileName(working_dir=system.System.get_working_dir())
o_file_time_stamp.select_image_folder()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Output Folder 

# + run_control={"frozen": false, "read_only": false}
o_file_time_stamp.select_export_folder()

# + run_control={"frozen": false, "read_only": false}

