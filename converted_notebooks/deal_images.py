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

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/deal_images)
#
# <img src='__docs/__all/notebook_rules.png' />

# # Select Your IPTS 

from __code.deal import Deal
from __code import system
system.System.select_working_dir()
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# ## Select Input Folder
# -

o_deal = Deal(working_dir=system.System.get_working_dir())
o_deal.select_input_folder()

# + [markdown] run_control={"frozen": false, "read_only": false}
# ## Select Output Folder 
# -

o_deal.select_output_folder()
