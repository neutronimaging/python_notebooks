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

# + [markdown] run_control={"frozen": false, "read_only": false}
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/tutorials/imaging-notebooks/water-intake-profile-calculator/)

# + [markdown] run_control={"frozen": false, "read_only": false}
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code import system
from __code.water_intake_profile_calculator import WaterIntakeProfileCalculator, WaterIntakeProfileSelector

system.System.select_working_dir(notebook='water_intake_profile_calculator')
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Python Import 

# + run_control={"frozen": false, "read_only": false}
# %gui qt

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Images to Process

# + run_control={"frozen": false, "read_only": false}
o_water = WaterIntakeProfileCalculator(working_dir=system.System.get_working_dir())
o_water.select_data()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Profile Region 

# + run_control={"frozen": false, "read_only": false}
o_gui = WaterIntakeProfileSelector(dict_data=o_water.dict_files)
o_gui.show()

# + run_control={"frozen": false, "read_only": false}

