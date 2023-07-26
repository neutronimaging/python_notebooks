# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.7
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# + [markdown] run_control={"frozen": false, "read_only": false}
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/tutorials/imaging-notebooks/from-attenuation-to-concentration/)

# + [markdown] run_control={"frozen": false, "read_only": false}
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code.from_attenuation_to_concentration import *

from __code import system
system.System.select_working_dir(notebook='from_attenuation_to_concentration')
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Data Folder

# + run_control={"frozen": false, "read_only": false}
o_convert = FromAttenuationToConcentration(working_dir=system.System.get_working_dir())
o_convert.select_folder()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Define conversion formula 

# + run_control={"frozen": false, "read_only": false}
o_convert.define_conversion_formula()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Converting Data 

# + run_control={"frozen": false, "read_only": false}
o_convert.converting_data()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Output Folder Location

# + run_control={"frozen": false, "read_only": false}
o_convert.select_output_folder()

# + run_control={"frozen": false, "read_only": false}










