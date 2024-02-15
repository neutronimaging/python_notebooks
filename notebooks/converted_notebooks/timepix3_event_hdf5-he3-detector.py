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
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/timepix3-event-hdf5-he3-detector/)
#
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code import system
from __code.timepix3_event_hdf5_he3_detector.timepix3_event_hdf5_he3_detector import Timepix3EventHdf5

import h5py

system.System.select_working_dir(facility='SNS', instrument='SNAP')
from __code.__all import custom_style
custom_style.style()

import matplotlib.pyplot as plt
# %matplotlib notebook

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Event HDF5 - He3 tube detectors
# -

o_event = Timepix3EventHdf5(working_dir=system.System.get_working_dir())
o_event.select_nexus()


