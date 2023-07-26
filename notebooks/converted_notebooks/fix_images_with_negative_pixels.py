# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.6
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/tutorials/imaging-notebooks/fix-images-with-negative-pixels/)
#
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS

# + run_control={"frozen": false, "read_only": false}
from __code.fix_images_with_negative_pixels import FixImages
# %matplotlib notebook

from __code import system
system.System.select_working_dir(notebook='fix_images_with_negative_pixels')
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Description

# + [markdown] run_control={"frozen": false, "read_only": false}
# 1. Load images
# 2. Display 
# 3. Change all negative value pixels to NaN
# 4. Give statistics of pixels changed in ROI selected
# 5. produce colorbar

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Images 

# + run_control={"frozen": false, "read_only": false}
_o_fix = FixImages(working_dir=system.System.get_working_dir())
_o_fix.select_images()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Turn off all negative values 

# + run_control={"frozen": false, "read_only": false}
_o_fix.load()
_o_fix.remove_negative_values()
_o_fix.display_images()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Display Images for Publication 

# + run_control={"frozen": false, "read_only": false}
# %matplotlib notebook

# + run_control={"frozen": false, "read_only": false}
_o_fix.display_images_pretty()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Export

# + run_control={"frozen": false, "read_only": false}
_o_fix.select_output_folder()

# + run_control={"frozen": false, "read_only": false}
_o_fix.export()

# + run_control={"frozen": false, "read_only": false}

