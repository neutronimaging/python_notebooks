# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/tutorials/imaging-notebooks/fix-images/)
#
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS

# + run_control={"frozen": false, "read_only": false}
import warnings
warnings.filterwarnings('ignore')

from __code.fix_images import FixImages

# %matplotlib notebook
from __code import system
system.System.select_working_dir(notebook='fix_images')

from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Images

# + run_control={"frozen": false, "read_only": false}
_o_fix = FixImages(working_dir=system.System.get_working_dir())
_o_fix.select_images()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Give statistics 

# + run_control={"frozen": false, "read_only": false}
_o_fix.load()
_o_fix.give_statistics()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Display Images and Histograms 

# + run_control={"frozen": false, "read_only": false}
_o_fix.display_and_fix()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Export Images

# + run_control={"frozen": false, "read_only": false}
_o_fix.select_folder_and_export_images()

# + run_control={"frozen": false, "read_only": false}

