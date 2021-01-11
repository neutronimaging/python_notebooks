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

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/display_counts_of_region_vs_stack)

# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
import warnings
warnings.filterwarnings('ignore')

from __code.ui_builder import UiBuilder
o_builder = UiBuilder(ui_name = 'ui_display_counts_of_region_vs_stack.ui')

from __code.display_counts_of_region_vs_stack import ImageWindow, DisplayCountsVsStack

from __code import system
system.System.select_working_dir()
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # UI setup

# + run_control={"frozen": false, "read_only": false}
# %gui qt

# + [markdown] cell_style="split" run_control={"frozen": false, "read_only": false}
# # Select stack folder

# + run_control={"frozen": false, "read_only": false}
o_display = DisplayCountsVsStack(working_dir=system.System.get_working_dir())
o_display.select_input_folder()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Launch UI

# + run_control={"frozen": false, "read_only": false}
_image = ImageWindow(display_counts_vs_stack=o_display)
_image.show()

# + run_control={"frozen": false, "read_only": false}

