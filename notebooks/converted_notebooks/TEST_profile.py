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
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/en/tutorial/notebooks/profile/)

# + [markdown] run_control={"frozen": false, "read_only": false}
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code.ui_builder import UiBuilder
o_builder = UiBuilder(ui_name = 'ui_profile.ui')

from __code import system
from __code.fileselector import FileSelection
from __code.profile import ProfileUi

system.System.select_working_dir()
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Python Import 

# + run_control={"frozen": false, "read_only": false}
# %gui qt

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Images to Process

# + run_control={"frozen": false, "read_only": false}
o_selection = FileSelection(working_dir=system.System.get_working_dir())
o_selection.select_data()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Launch UI 

# + run_control={"frozen": false, "read_only": false}
o_profile = ProfileUi(working_dir=system.System.get_working_dir(), 
                                         data_dict=o_selection.data_dict['sample'])
o_profile.show()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # DEBUG

# + run_control={"frozen": false, "read_only": false}
from __code.ui_builder import UiBuilder
o_builder = UiBuilder(ui_name = 'ui_profile.ui')

from __code import system
from __code.fileselector import FileSelection
from __code.profile import ProfileUi

# + run_control={"frozen": false, "read_only": false}
# %gui qt

# + run_control={"frozen": false, "marked": true, "read_only": false}
import glob
import os
file_dir = '/Volumes/my_book_thunderbolt_duo/IPTS/IPTS-20139-Hao-Liu/05-07-18_LFR_normalized_light_version/' #MacPro
#file_dir = '/Users/j35/IPTS/charles/'

list_files = glob.glob(file_dir + '*.tif') 

o_selection = FileSelection()
o_selection.load_files(list_files)

o_profile = ProfileUi(working_dir=os.path.dirname(list_files[0]),
                      data_dict=o_selection.data_dict['sample'])
o_profile.show()


# + run_control={"frozen": false, "read_only": false}


# + run_control={"frozen": false, "read_only": false}

