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

# + [markdown] run_control={"frozen": false, "read_only": false}
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/outliers_filtering_tool)

# + [markdown] run_control={"frozen": false, "read_only": false}
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS

# + run_control={"frozen": false, "read_only": false}
import warnings
warnings.filterwarnings('ignore')

from __code.outliers_filtering.gamma_filtering_tool import Interface, InterfaceHandler

from __code import system
system.System.select_working_dir()
from __code.__all import custom_style
custom_style.style()

# + run_control={"frozen": false, "read_only": false}
# %gui qt

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Images

# + run_control={"frozen": false, "read_only": false}
o_template = InterfaceHandler(working_dir=system.System.get_working_dir())
o_template.select_all_images()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Load and Display Images

# + run_control={"frozen": false, "read_only": false}
o_interface = Interface(list_of_files = o_template.get_list_of_files())
o_interface.show()
# -


