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

# + [markdown] run_control={"frozen": false, "read_only": false}
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/tutorials/imaging-notebooks/display-file-name-vs-time-stamp/)

# + [markdown] run_control={"frozen": false, "read_only": false}
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code.display_file_names_vs_time_stamp import DisplayFileNamesVsTimeStamp

# %matplotlib notebook

from __code import system
system.System.select_working_dir(notebook='display_file_names_vs_time_stamp')
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Images

# + run_control={"frozen": false, "read_only": false}
o_file_time_stamp = DisplayFileNamesVsTimeStamp(working_dir=system.System.get_working_dir())
o_file_time_stamp.select_image_folder()

# + [markdown] run_control={"frozen": false, "read_only": false}
# #  Display Time Stamp (relative and absolute offsets)

# + run_control={"frozen": false, "read_only": false}
o_file_time_stamp.display()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # List Files Loaded 

# + run_control={"frozen": false, "read_only": false}
o_file_time_stamp.print_result()

# + run_control={"frozen": false, "read_only": false}


# + run_control={"frozen": false, "read_only": false}

