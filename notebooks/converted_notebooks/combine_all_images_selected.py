# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/combine_all_images_selected)
#
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code.combine_images import CombineImages
from __code import system
system.System.select_working_dir()
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Images to Merge 

# + run_control={"frozen": false, "read_only": false}
o_merge = CombineImages(working_dir=system.System.get_working_dir())
o_merge.select_files()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Merging Method

# + run_control={"frozen": false, "read_only": false}
o_merge.how_to_combine()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Output Folder 

# + run_control={"frozen": false, "read_only": false}
o_merge.select_output_folder()

# + run_control={"frozen": false, "read_only": false}
o_merge.define_output_filename()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Merging 

# + run_control={"frozen": false, "read_only": false}
o_merge.merging()
# -


