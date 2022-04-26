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

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/group_images_by_cycle_for_grating_experiment)
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
import warnings
warnings.filterwarnings('ignore')

from __code.group_images_by_cycle_for_grating_experiment.group_images import GroupImages
from __code import system
system.System.select_working_dir()
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Data to Sort

# + run_control={"frozen": false, "read_only": false}
o_group = GroupImages(working_dir=system.System.get_working_dir())
o_group.select_data_to_sort()
# -

# # Select Metadata to Use for Sorting 

o_group.select_metadata_to_use_for_sorting()

# # Grouping 

o_group.grouping()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Output Folder
#
# A folder will be created in this output folder and named after the input folder name.

# + run_control={"frozen": false, "read_only": false}
o_group.select_output_folder()
# -

# # Generate Angel Configuration File (Excel) 

# %gui qt

o_group.generate_angel_configuration_file()
