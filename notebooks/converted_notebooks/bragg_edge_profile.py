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
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/tutorials/imaging-notebooks/bragg-edge/bragg-edge-profile/)
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code import system
from __code.bragg_edge.bragg_edge_normalization import BraggEdge
from __code.bragg_edge.bragg_edge import Interface

system.System.select_working_dir(facility='SNS', instrument='VENUS', notebook='bragg_edge_profile')
from __code.__all import custom_style
custom_style.style()

from plotly.offline import plot, init_notebook_mode, iplot
init_notebook_mode()
# -

# ## Prepare UI engine 

# + run_control={"frozen": false, "read_only": false}
# %gui qt

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Normalized Data Input Folder
#
# Data and time spectra files will be loaded

# + run_control={"frozen": false, "read_only": false}
o_bragg = BraggEdge(working_dir=system.System.get_working_dir())
o_bragg.select_working_folder()
# -

# # Calculate Bragg edge profile

# + [markdown] run_control={"frozen": false, "read_only": false}
# ## Define Experiment Setup

# + run_control={"frozen": false, "read_only": false}
o_bragg.exp_setup()
# -

# ## Calculate signal of sample region

# ### Select how many random files to use to select sample position

o_bragg.how_many_data_to_use_to_select_sample_roi()

# ### Select the sample position 

o_interface_sample = Interface(data=o_bragg.get_image_to_use_for_display())
o_interface_sample.show()

# ## Calculate

# o_bragg.calculate_counts_vs_file_index_of_regions_selected(list_roi=o_interface.list_roi)
o_bragg.calculate_counts_vs_file_index_of_regions_selected(list_roi=o_interface_sample.roi_selected)
o_bragg.load_time_spectra()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Display Bragg Edges vs Signal
# -

# Run the next cell **only if** you want to display the signal Counts vs lambda 

# + run_control={"frozen": false, "read_only": false}
o_bragg.plot()
# -
# # Export ASCII Data 

o_bragg.select_output_data_folder()


