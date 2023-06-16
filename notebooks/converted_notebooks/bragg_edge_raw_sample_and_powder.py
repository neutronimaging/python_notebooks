# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# + [markdown] run_control={"frozen": false, "read_only": false}
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/bragg_edge_raw_sample_and_powder)
#
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code import system
from __code.bragg_edge.bragg_edge_raw_sample_and_powder import BraggEdge
from __code.bragg_edge.bragg_edge import Interface

system.System.select_working_dir(facility='SNS', instrument='SNAP', notebook='bragg_edge_raw_sample_and_powder')
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

# # Select Background Region

# + [markdown] run_control={"frozen": false, "read_only": false}
# ### Select how many random files to use to select various ROIs

# + run_control={"frozen": false, "read_only": false}
o_bragg.how_many_data_to_use_to_select_sample_roi()

# + [markdown] run_control={"frozen": false, "read_only": false}
# ### Select background region in integrated image

# + run_control={"frozen": false, "read_only": false}
o_bragg.define_integrated_sample_to_use()
o_background = Interface(data=o_bragg.final_image)
o_background.show()
# -

# # Normalize Data 

o_bragg.normalization(o_background=o_background)

# # Powder Element(s) to Use to Compare the Bragg Edges  

o_bragg.list_elements()

# ## List Bragg Edges 

o_bragg.list_powder_bragg_edges()

# # Select Sample ROI 

o_sample = Interface(data=o_bragg.final_image)
o_sample.show()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Define Experiment Setup

# + run_control={"frozen": false, "read_only": false}
o_bragg.exp_setup()
# -

# # Calculate Bragg Edges Data 

o_bragg.calculate_counts_vs_file_index_of_regions_selected(list_roi=o_sample.list_roi)
o_bragg.load_time_spectra()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Display Bragg Edges vs Signal
# -

# Run the next cell **only if** you want to display the signal Counts vs lambda 

# + run_control={"frozen": false, "read_only": false}
o_bragg.plot()
# -
# # Export Data 

o_bragg.select_output_data_folder()

o_bragg.select_output_table_folder()


