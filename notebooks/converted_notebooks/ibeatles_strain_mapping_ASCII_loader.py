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

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/tutorials/imaging-notebooks/ibeatles/ibeatles-strain-mapping-ascii_loader/)
#
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
import warnings
warnings.filterwarnings('ignore')

from __code.ibeatles_strain_mapping_ascii_loader.main import Main
from __code import system
system.System.select_working_dir()
from __code.__all import custom_style
custom_style.style()

# %matplotlib notebook

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select ASCII file created in iBeatles (strain step)

# + run_control={"frozen": false, "read_only": false}
o_strain_display = Main(working_dir = system.System.get_working_dir())
o_strain_display.select_ascii_file()
# -

# # Display data 

# + run_control={"frozen": false, "read_only": false}
o_strain_display.process_data()
o_strain_display.display()   
# -


