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
from __code.venus_monitor_hdf5.main import VenusMonitorHdf5

import h5py
import numpy as np

system.System.select_working_dir(facility='SNS', instrument='VENUS')
from __code.__all import custom_style
custom_style.style()

import matplotlib.pyplot as plt
# %matplotlib notebook
# -

# %matplotlib inline

# # Define settings

o_event = VenusMonitorHdf5(working_dir=system.System.get_working_dir())
o_event.define_settings()

o_event.record_settings()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Event NeXus
# -

o_event.select_event_nexus()
