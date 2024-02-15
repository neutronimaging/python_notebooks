# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/tutorials/imaging-notebooks/combine/combine-images-sequentially-using-the-metadata/)
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code.sequential_combine_images_using_metadata import SequentialCombineImagesUsingMetadata
from __code import system
system.System.select_working_dir(notebook='sequential_combine_images_using_metadata')
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Folder containing all images to merge 

# + run_control={"frozen": false, "read_only": false}
o_merge = SequentialCombineImagesUsingMetadata(working_dir=system.System.get_working_dir())
o_merge.select_folder()
# -

# # Select Metadata to match 

# Only sequential runs having the **same metadata you are going to select** will be combined

o_merge.display_metadata_list()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Merging Method

# + run_control={"frozen": false, "read_only": false}
o_merge.how_to_combine()
# -

# # Create merging list - for checking purpose

o_merge.create_merging_list()

# Check merging list

o_merge.recap_merging_list()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Output Folder and Merge

# + run_control={"frozen": false, "read_only": false}
o_merge.select_output_folder_and_merge()
# -


