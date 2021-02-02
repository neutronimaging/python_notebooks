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

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/panoramic_stitching_for_tof/#activate-search)
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
import warnings
warnings.filterwarnings('ignore')

from __code.panoramic_stitching_for_tof.panoramic_stitching_for_tof import PanoramicStitching
from __code import system
system.System.select_working_dir()
from __code.__all import custom_style
custom_style.style()
# -

# %gui qt

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Input Folder(s)
#
# Select all the folders containing the images to stitch. Ideally, those folders have been created by the notebook [group_images_by_cycle_for_panoramic_stitching](group_images_by_cycle_for_panoramic_stitching.ipynb)

# + run_control={"frozen": false, "read_only": false}
o_stitch = PanoramicStitching(working_dir=system.System.get_working_dir())
o_stitch.select_input_folders()
# -


