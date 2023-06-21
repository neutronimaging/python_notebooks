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

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/bin_images)
#
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code.bin_images import BinHandler
from __code import system
system.System.select_working_dir(notebook='bin_images')
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Images to Rebin

# + run_control={"frozen": false, "read_only": false}
o_bin = BinHandler(working_dir = system.System.get_working_dir())
o_bin.select_images()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Bin Parameter 

# + run_control={"frozen": false, "read_only": false}
o_bin.select_bin_parameter()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Export 

# + run_control={"frozen": false, "read_only": false}
o_bin.select_export_folder()
# -


