# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.5.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# + [markdown] run_control={"frozen": false, "read_only": false}
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/bragg_edge_normalization_and_profile_extractor/#activate-search)
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code import system
from __code.bragg_edge.bragg_edge_normalization import BraggEdge
from __code.bragg_edge.bragg_edge import Interface

system.System.select_working_dir(facility='SNS', instrument='SNAP')
from __code.__all import custom_style
custom_style.style()

from plotly.offline import plot, init_notebook_mode, iplot
init_notebook_mode()
# -

# ## Prepare UI engine 

# + run_control={"frozen": false, "read_only": false}
# %gui qt

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Raw Data Input Folder
#
# Data and time spectra files will be loaded

# + run_control={"frozen": false, "read_only": false}
o_bragg = BraggEdge(working_dir=system.System.get_working_dir())
o_bragg.select_working_folder()
# -

# # Select Open Beam Input Folder 

o_bragg.select_ob_folder()

# # Normalization

# + [markdown] run_control={"frozen": false, "read_only": false}
# ### Select how many random files to use to select sample position

# + run_control={"frozen": false, "read_only": false}
o_bragg.how_many_data_to_use_to_select_sample_roi()

# + [markdown] run_control={"frozen": false, "read_only": false}
# ### Select background region
# -

# In order to improve the normalization you have the option to select a region in your images that **you know for sure is away from the sample**. The algorithm will use that **background** region to match it with the same region of the open beam (OB) images.

# + run_control={"frozen": false, "read_only": false}
o_interface = Interface(data=o_bragg.get_image_to_use_for_display())
o_interface.show()
# -

# ## Perform normalization 

o_bragg.normalization(list_rois=o_interface.roi_selected)

# ## Export normalized data 

o_bragg.export_normalized_data()

# # Calculate Bragg edge profile

# + [markdown] run_control={"frozen": false, "read_only": false}
# ## Define Experiment Setup

# + run_control={"frozen": false, "read_only": false}
o_bragg.exp_setup()
# -

# ## Define the position of your sample 

o_interface_sample = Interface(data=o_bragg.final_image)
o_interface_sample.show()

# ## Calculate signal of sample region

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


