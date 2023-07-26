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
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/tutorial/notebooks/timepix3_from_event_to_hito_hdf5)
#
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code import system
from __code.timepix3_from_event_to_histo_hdf5.timepix3_from_event_to_histo_hdf5 import Timepix3FromEventToHistoHdf5

import h5py
import numpy as np

system.System.select_working_dir(facility='SNS', instrument='SNAP')
from __code.__all import custom_style
custom_style.style()

import matplotlib.pyplot as plt
# %matplotlib notebook

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Event NeXus
# -

o_event = Timepix3FromEventToHistoHdf5(working_dir=system.System.get_working_dir())
o_event.select_event_nexus()

# # Manually loading the data

with h5py.File(o_event.input_nexus_file_name, 'r') as nxs:
    o_event.x_array = np.array(nxs['events']['x'])
    o_event.y_array = np.array(nxs['events']['y'])
    o_event.tof_array = np.array(nxs['events']['tof_ns'])

# # Some statistics 

o_event.display_infos()

# # Define MCP detector size 

o_event.define_detector()

# # Binning data (Zzz)

o_event.select_binning_parameter()

# This may take some time, be patient!

o_event.bins()

# # Display integrated stack 

o_event.display_integrated_stack()

# # Display slices 

o_event.display_slices()

# # Export Histogram HDF5 

o_event.define_output_filename()

o_event.select_output_location()


