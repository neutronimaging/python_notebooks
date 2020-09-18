# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.5.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/normalization_with_simplify_selection)
#
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code.normalization_with_simplify_selection import NormalizationWithSimplifySelection
from __code import system
system.System.select_working_dir()
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select List of Images to Normalize 
# -

# Program will create a full table of the normalization workflow according to the **acquisition time** and **instrument configurations**.
#
# Change the time range if needed!

# + run_control={"frozen": false, "read_only": false}
o_which = NormalizationWithSimplifySelection(working_dir=system.System.get_working_dir())
o_which.select_sample_images_and_create_configuration()
# -

# # Normalization workflow

o_which.checking_normalization_workflow()

# # Select Output Folder 

o_which.select_output_folder()

o_which.debugging_o_load.export(folder="/Users/j35/Desktop/Aug25_2020_60.0_config0", file_type='tif')


