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
# <img src='__docs/__all/prototype.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/normalization_batch)

# + [markdown] run_control={"frozen": false, "read_only": false}
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code.normalization_batch import *

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

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Background Region 

# + run_control={"frozen": false, "read_only": false}
o_norm = sample_panel.o_norm_handler
o_gui = Interface(o_norm=o_norm.o_norm)
o_gui.show()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Output Folder

# + run_control={"frozen": false, "read_only": false}
o_norm.select_export_folder()

# + run_control={"frozen": false, "read_only": false}
o_norm.export(rois=o_gui.roi_selected)

# + run_control={"frozen": false, "read_only": false}

