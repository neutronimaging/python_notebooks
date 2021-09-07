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
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/wave_front_dynamics/)

# + [markdown] run_control={"frozen": false, "read_only": false}
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS

# + run_control={"frozen": false, "read_only": false}
import warnings
warnings.filterwarnings('ignore')

from __code.wave_front_dynamics.wave_front_dynamics import WaveFrontDynamics, WaveFrontDynamicsUI
from __code import system
system.System.select_working_dir()
from __code.__all import custom_style
custom_style.style()
# -

# %gui qt

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Profile Files to Process
#
# list of notebooks that create such files
# * [radial_profile](radial_profile.ipynb)
# -

o_wave = WaveFrontDynamics(working_dir=system.System.get_working_dir())
o_wave.select_data()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Launch User Interface

# + run_control={"frozen": false, "read_only": false}
o_ui = WaveFrontDynamicsUI(working_dir=system.System.get_working_dir(),
                           wave_front_dynamics=o_wave)
o_ui.show()
# -


