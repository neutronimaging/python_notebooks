# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.15.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# + [markdown] run_control={"frozen": false, "read_only": false}
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/tutorials/imaging-notebooks/timepix3/timepix3-histogram-hdf5-mcp-detector/)
#
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code import system
from __code.timepix3_histo_hdf5_mcp_detector.timepix3_histo_hdf5_mcp_detector import Timepix3HistoHdf5McpDetector

system.System.select_working_dir(facility='SNS', instrument='SNAP')
from __code.__all import custom_style
custom_style.style()

import matplotlib.pyplot as plt
# %matplotlib notebook
# -

# # Prepare UI engine 

# %gui qt

# # Select Histo MCP HDF5 File  

o_timepix3 = Timepix3HistoHdf5McpDetector(working_dir=system.System.get_working_dir())
o_timepix3.hdf5_or_config_file_input()

# # Integrate Signal

o_timepix3.preview_integrated_stack()

# # Select Region of Interest (ROI) for Each Image

o_timepix3.select_roi()

# # Display profile of ROI(s)
# If more than 1 region was selected, the regions will be combined.

o_timepix3.calculate_and_display_profile()

# # Fit Bragg peak

# ## Select Peak to fit

o_timepix3.select_peak_to_fit()

# ## fit peak 

o_timepix3.fitting()

# # Saving session

o_timepix3.saving_session()


