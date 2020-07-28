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
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/normalization)
#
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code.normalization import *

from __code.ui_builder import UiBuilder
o_builder = UiBuilder(ui_name = 'ui_roi_selection.ui')
from __code.roi_selection_ui import Interface

from __code import system
system.System.select_working_dir()
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Python Import

# + run_control={"frozen": false, "read_only": false}
# %gui qt

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Images (Sample, OB, and DF)

# + run_control={"frozen": false, "read_only": false}
files = Files()
sample_panel = SampleSelectionPanel(working_dir=system.System.get_working_dir())
sample_panel.init_ui(files=files)
wizard = WizardPanel(sample_panel=sample_panel)
# -

#DEBUGGING
o_norm = sample_panel.o_norm_handler
o_norm.o_norm.data['ob']['data']

o_norm.o_norm.data['sample']['data']

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Background Region 

# + run_control={"frozen": false, "read_only": false}
o_norm = sample_panel.o_norm_handler
o_gui = Interface(o_norm=o_norm.o_norm)
o_gui.show()
# -

o_norm.debugging_roi

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Normalization

# + run_control={"frozen": false, "read_only": false}
o_norm.run_normalization(dict_roi=o_gui.roi_selected)

# +
#DEBUGGING
o_norm.o_norm.data['sample']


# -

o_norm.o_norm.get_normalized_data()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Export 

# + run_control={"frozen": false, "read_only": false}
o_norm.select_export_folder(ipts_folder=sample_panel.ipts_dir)

# + run_control={"frozen": false, "read_only": false}
o_norm.export()
# -





o_norm.debugging_roi.



# +
from NeuNorm.normalization import Normalization
from NeuNorm.roi import ROI

from pathlib import Path

import matplotlib.pyplot as plt
# %matplotlib notebook
# -

my_roi = ROI(x0=118, y0=18, x1=259, y1=489)
o_norm.o_norm.normalization(roi=my_roi)

#o_norm.o_norm.data['ob']
plt.imshow(o_norm.o_norm.data['ob']['data'][0])

# +
divided = o_norm.data.sample[0] / o_norm.data.ob[0]
plt.figure()
plt.imshow(divided)



# -

import matplotlib.pyplot as plt
# %matplotlib notebook

# + run_control={"frozen": false, "read_only": false}
plt.imshow(o_norm.normalized_data_array[0])
# -


