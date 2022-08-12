# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/shifting_time_offset/)
#
# <img src='__docs/__all/notebook_rules.png' />

# # Select Your IPTS 

# +
from __code.select_files_and_folders import SelectFiles, SelectFolder
from __code.shifting_time_offset import ShiftTimeOffset

from __code import system
system.System.select_working_dir()
from __code.__all import custom_style
custom_style.style()
# -

# # Select Folder

o_shift = ShiftTimeOffset()
o_select = SelectFolder(system=system, is_input_folder=True, next_function=o_shift.display_counts_vs_time)

# # Repeat on other folders?

o_other_folders = SelectFolder(working_dir=o_shift.working_dir,
                              is_input_folder=True,
                              multiple_flags=True,
                              next_function=o_shift.selected_other_folders)

# # Output Images 

o_shift.offset_images()


