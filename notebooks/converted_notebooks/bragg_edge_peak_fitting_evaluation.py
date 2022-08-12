# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# + [markdown] run_control={"frozen": false, "read_only": false}
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/bragg_edge_peak_fitting)
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code import system
from __code.bragg_edge.bragg_edge_peak_fitting_evaluation import BraggEdge, Interface

system.System.select_working_dir(facility='SNS', instrument='VENUS')
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

# # Select Open Beam Data Input folder 

# + jupyter={"outputs_hidden": true}
o_bragg.select_ob_folder()
# -

# # Select sample region and peak to fit

# ### Select how many random files to use to select region to fit

o_bragg.how_many_data_to_use_to_select_sample_roi()

# ### fit ui 

o_interface = Interface(o_bragg=o_bragg, spectra_file=o_bragg.spectra_file)
o_interface.show()

# # DEBUGGING

from __code import system
from __code.bragg_edge.peak_fitting_evaluation.bragg_edge_peak_fitting import BraggEdge, Interface

# %gui qt

# +
import os

# small data set
# data_path = "/Volumes/G-DRIVE/IPTS/VENUS/shared/testing_normalized/"
# spectra_file = os.path.join(data_path, "Image019_Spectra.txt")

# full data set
#data_path = "/Volumes/G-DRIVE/IPTS/SNAP/Si_normalized/Si_powder_1_Angs_20C_corrected_normalized"
#spectra_file = os.path.join(data_path, "normalized_Spectra.txt")
data_path = "/Volumes/G-DRIVE/IPTS/IPTS-26171-testing_ibeatles/10_InconelPowder_1.5Hrs_Corrected_normalized/"
spectra_file = "/Volumes/G-DRIVE/IPTS/IPTS-26171-testing_ibeatles/10_InconelPowder_1.5Hrs_Corrected_normalized/20210910_Run_52256_InconelPowder_0008_0646026_Spectra.txt"

import glob
list_data = glob.glob(data_path + "*.tif")
assert os.path.exists(spectra_file)

o_bragg = BraggEdge(working_dir=data_path)
o_bragg.load_data(data_path)
# -

o_interface = Interface(o_bragg=o_bragg,
                        working_dir=data_path,
                        spectra_file=spectra_file)
o_interface.show()











# # DEBUGGING using import straight 

from __code import system
from __code.bragg_edge.peak_fitting_evaluation.bragg_edge_peak_fitting import BraggEdge, Interface

# %gui qt

data_path = "/Volumes/G-Drive/IPTS/SNAP/Si_normalized/Si_powder_1_Angs_20C_corrected_normalized"
o_interface = Interface(working_dir=data_path)
o_interface.show()






