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
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/tutorials/imaging-notebooks/venus_monitor_hdf5/)
#
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS 

# +
from __code import system
from __code.venus_list_of_nexus_with_pc_above_threshold.main import VenusNexusListPCAboveThreshold

import h5py
import numpy as np

system.System.select_working_dir(facility='SNS', instrument='VENUS')
from __code.__all import custom_style
custom_style.style()

import matplotlib.pyplot as plt
# %matplotlib notebook
# -

# %matplotlib notebook

# # Define settings

o_event = VenusNexusListPCAboveThreshold(working_dir=system.System.get_working_dir())
o_event.proton_charge_threshold()

o_event.select_list_nexus()

# # Export this list of NeXus with proton charge above threshold

o_event.export_good_nexus()


