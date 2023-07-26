# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.6
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# + [markdown] run_control={"frozen": false, "read_only": false}
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/tutorials/imaging-notebooks/bragg-edge/bragg-edge-normalization/)
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code import system
from __code.bragg_edge.bragg_edge_normalization import BraggEdge

system.System.select_working_dir(facility='SNS', instrument='SNAP', notebook='bragg_edge_normalization')
from __code.__all import custom_style
custom_style.style()

from plotly.offline import plot, init_notebook_mode, iplot
init_notebook_mode()
# -

# ## Prepare UI Engine 

# + run_control={"frozen": false, "read_only": false}
# %gui qt

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Raw Data Input Folder
# time spectra files will be loaded

# + run_control={"frozen": false, "read_only": false}
o_bragg = BraggEdge(working_dir=system.System.get_working_dir())
o_bragg.select_working_folder()
# -

# # Select mode of normalization 

o_bragg.normalization_settings_widgets()

# # Export Normalized Data and Time Spectra File

o_bragg.normalization()




