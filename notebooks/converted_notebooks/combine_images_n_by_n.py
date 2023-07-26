# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.7
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/tutorials/imaging-notebooks/combine/combine-images-n-by-n/)
#
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code.combine_images_n_by_n.combine_images_n_by_n import CombineImagesNByN as CombineImages
from __code import system
system.System.select_working_dir(notebook='combine_images_n_by_n')
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Folder with Images to Combine 

# + run_control={"frozen": false, "read_only": false}
o_merge = CombineImages(working_dir=system.System.get_working_dir())
o_merge.select_images()
# -

# # Sorting the Files 

o_merge.sorting_the_files()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Merging Arithmetic Method

# + run_control={"frozen": false, "read_only": false}
o_merge.how_to_combine()
# -

# # How many files do you want to combine together?
#
# ex: Selecting **2** will combine the first **2**, then the following **2**...

o_merge.how_many_files()

# # Preview of how the files will be combined and renamed

o_merge.preview_result()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Output Folder 

# + run_control={"frozen": false, "read_only": false}
o_merge.select_output_folder()
# -


