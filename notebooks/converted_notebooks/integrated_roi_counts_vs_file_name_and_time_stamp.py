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
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/tutorials/imaging-notebooks/integrated-roi-counts-vs-file-name-and-time-stamp/)
#
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Setup Environment 

# + run_control={"frozen": false, "read_only": false}
# %gui qt

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select your IPTS 

# + run_control={"frozen": false, "read_only": false}
import warnings
warnings.filterwarnings('ignore')

from __code.ui_builder import UiBuilder
o_builder = UiBuilder(ui_name = 'ui_integrated_roi_counts_vs_file_name_and_time_stamp.ui')

from __code import system
from __code.ipywe.myfileselector import FileSelection
from __code.integrated_roi_counts_vs_file_name_and_time_stamp import IntegratedRoiUi

system.System.select_working_dir(notebook='integrated_roi_counts_vs_file_name_and_time_stamp')
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Images to Process

# + run_control={"frozen": false, "read_only": false}
o_selection = FileSelection(working_dir=system.System.get_working_dir())
o_selection.select_data()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Launch UI 

# + run_control={"frozen": false, "read_only": false}
o_integration = IntegratedRoiUi(working_dir=system.System.get_working_dir(), 
                            data_dict=o_selection.data_dict['sample'])
o_integration.show()

# + run_control={"frozen": false, "read_only": false}


# + run_control={"frozen": false, "read_only": false}

