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

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/combine_images_n_by_n)
#
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code.combine_images_n_by_n import CombineImagesNByN as CombineImages
from __code import system
system.System.select_working_dir()
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Folder with Images to Combine 

# + run_control={"frozen": false, "read_only": false}
o_merge = CombineImages(working_dir=system.System.get_working_dir())
o_merge.select_folder()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Merging Arithmetic Method

# + run_control={"frozen": false, "read_only": false}
o_merge.how_to_combine()
# -

# # How many files do you want to combine together?
#
# ex: Selecting **2** will combine the first **2**, then the following **2**...

o_merge.how_many_files()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Output Folder 

# + run_control={"frozen": false, "read_only": false}
o_merge.select_output_folder()
# -




