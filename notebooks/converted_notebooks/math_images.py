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

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/math_images)
#
# <img src='__docs/__all/notebook_rules.png' />

# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code.math_images import MathImages
from __code import system
system.System.select_working_dir()
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Images to Operate On

# + run_control={"frozen": false, "read_only": false}
o_math = MathImages(working_dir=system.System.get_working_dir())
o_math.select_files()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Image to Use in Operation

# + run_control={"frozen": false, "read_only": false}
o_math.select_target_image()

# + [markdown] run_control={"frozen": false, "read_only": false}
# ##  Operation to Use

# + run_control={"frozen": false, "read_only": false}
o_math.which_math()
# -

# ## Recap

o_math.recap()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Output Folder 

# + run_control={"frozen": false, "read_only": false}
o_math.select_output_folder()
# -


