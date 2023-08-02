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
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/tutorials/imaging-notebooks/registration/)

# + [markdown] run_control={"frozen": false, "read_only": false}
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select your IPTS 

# + run_control={"frozen": false, "read_only": false}
import warnings
warnings.filterwarnings('ignore')

from __code.registration.file_selection import FileSelection
from __code.registration.registration import RegistrationUi

from __code import system
system.System.select_working_dir(notebook='registration')
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Python Import 

# + run_control={"frozen": false, "read_only": false}
# %gui qt

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Images to Process
# -

# DEBUGGING
working_dir = "/Users/j35/HFIR/CG1D/IPTS-30750/23_06_09_left/"
#working_dir = "/Volumes/JeanHardDrive/HFIR/CG1D/IPTS-30750/23_06_09_left_registered/"
o_selection = FileSelection(working_dir=working_dir)
o_selection.select_data()


# + run_control={"frozen": false, "read_only": false}
# o_selection = FileSelection(working_dir=system.System.get_working_dir())
# o_selection.select_data()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Launch Registration UI 

# + run_control={"frozen": false, "read_only": false}
o_registration = RegistrationUi(data_dict=o_selection.data_dict['sample'])
o_registration.show()

# + run_control={"frozen": false, "read_only": false}

