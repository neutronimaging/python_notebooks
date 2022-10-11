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

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/combine_folders)
#
# <img src='__docs/__all/notebook_rules.png' />

# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code.combine_folders import CombineFolders
from __code import system
system.System.select_working_dir()
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Folders to Merge 

# + run_control={"frozen": false, "read_only": false}
o_merge = CombineFolders(working_dir=system.System.get_working_dir())
o_merge.select_folders()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Merging Method

# + [markdown] run_control={"frozen": false, "read_only": false}
# ## How many folders do you want to combine together

# + [markdown] run_control={"frozen": false, "read_only": false}
# ex: **2** will combine the first 2 folders selected, then the next 2, ....

# + run_control={"frozen": false, "read_only": false}
o_merge.how_many_folders()

# + [markdown] run_control={"frozen": false, "read_only": false}
# ##  How do you want to combine them

# + run_control={"frozen": false, "read_only": false}
o_merge.how_to_combine()
# -

# ## Do you want to copy over extra files (.txt, ...)
#
# If **yes**, the first folder selected will be the source of those files

o_merge.extra_files()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Output Folder 

# + run_control={"frozen": false, "read_only": false}
o_merge.select_output_folder()
# -


