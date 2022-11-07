# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# + [markdown] run_control={"frozen": false, "read_only": false}
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/circular_profile_of_a_ring/)

# + [markdown] run_control={"frozen": false, "read_only": false}
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS

# + run_control={"frozen": false, "read_only": false}
import warnings
warnings.filterwarnings('ignore')

from __code.circular_profile_of_a_ring.interface_handler import InterfaceHandler
from __code.circular_profile_of_a_ring.circular_profile_of_a_ring import CircularProfileOfARing

from __code import system
system.System.select_working_dir()
from __code.__all import custom_style
custom_style.style()

# + run_control={"frozen": false, "read_only": false}
# %gui qt

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select folder containing reconstructed data

# + run_control={"frozen": false, "read_only": false}
o_selection = CircularProfileOfARing(working_dir=system.System.get_working_dir())
o_selection.select_input_folder()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Launch User Interface

# + run_control={"frozen": false, "read_only": false}
o_select = InterfaceHandler(working_dir=system.System.get_working_dir(), 
                            o_norm=o_selection.o_norm)
# -


