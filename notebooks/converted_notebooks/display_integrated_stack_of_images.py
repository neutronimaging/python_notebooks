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

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/display_integrated_stack_of_images)
#
# <img src='__docs/__all/notebook_rules.png' />

# # Select Your IPTS 

# +
from __code.display_integrated_stack_of_images import DisplayIntegratedStackOfImages

# %matplotlib notebook

from __code import system
system.System.select_working_dir()
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Input Folder
# -

o_integrated = DisplayIntegratedStackOfImages(working_dir=system.System.get_working_dir())
o_integrated.select_input_folder()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Load Stack
# -

o_integrated.display_integrated_stack()


