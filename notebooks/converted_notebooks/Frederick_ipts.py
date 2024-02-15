# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# + [markdown] run_control={"frozen": false, "read_only": false}
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/frederick_ipts/)

# + [markdown] run_control={"frozen": false, "read_only": false}
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select IPTS

# + run_control={"frozen": false, "read_only": false}
from __code.frederick_ipts import FrederickIpts

from __code.ui_builder import UiBuilder
o_builder = UiBuilder(ui_name = 'ui_file_metadata_display.ui')
from __code.file_metadata_display import Interface

from __code import system
system.System.select_working_dir()
from __code.__all import custom_style
custom_style.style()
# -

# %gui qt

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Files 

# + run_control={"frozen": false, "read_only": false}
o_fred = FrederickIpts(working_dir = system.System.get_working_dir())
o_fred.select_files()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Display images 

# + run_control={"frozen": false, "read_only": false}
o_gui = Interface(exp_dict=o_fred.exp_dict)
o_gui.show()

# + run_control={"frozen": false, "read_only": false}

