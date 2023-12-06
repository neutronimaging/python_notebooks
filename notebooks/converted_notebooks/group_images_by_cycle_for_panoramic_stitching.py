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

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/tutorials/imaging-notebooks/group-images-per-cycle-for-panoramic-stitching/)
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code.group_images_by_cycle_for_panoramic_stitching.group_images import GroupImages
from __code import system
system.System.select_working_dir(notebook='group_images_by_cycle_for_panoramic_stitching')
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Input Folder

# + run_control={"frozen": false, "read_only": false}
o_group = GroupImages(working_dir=system.System.get_working_dir())
o_group.select_input_folder()
# -

# # Sort files 

o_group.how_to_sort_files()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Output Folder
#
# A folder will be created in this output folder and named after the input folder name.

# + run_control={"frozen": false, "read_only": false}
o_group.select_output_folder()
# -


