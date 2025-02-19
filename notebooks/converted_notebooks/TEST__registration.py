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
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/en/tutorial/notebooks/registration/)

# + [markdown] run_control={"frozen": false, "read_only": false}
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code.ui_builder import UiBuilder
o_builder = UiBuilder(ui_name = 'ui_registration.ui')
o_builder = UiBuilder(ui_name = 'ui_registration_tool.ui')
o_builder = UiBuilder(ui_name = 'ui_registration_auto_confirmation.ui')
o_builder = UiBuilder(ui_name = 'ui_registration_markers.ui')
o_builder = UiBuilder(ui_name = 'ui_registration_profile.ui')
o_builder = UiBuilder(ui_name = 'ui_registration_profile_settings.ui')

from __code import system
from __code.registration.registration import RegistrationFileSelection, RegistrationUi

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
o_selection = RegistrationFileSelection(working_dir=system.System.get_working_dir())
o_selection.select_data()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Launch Registration UI 

# + run_control={"frozen": false, "read_only": false}
o_registration = RegistrationUi(data_dict=o_selection.data_dict['sample'])
o_registration.show()

# + [markdown] run_control={"frozen": false, "read_only": false}
# DEBUGGING

# + run_control={"frozen": false, "read_only": false}
# %gui qt

# + run_control={"frozen": false, "read_only": false}
from __code.ui_builder import UiBuilder
o_builder = UiBuilder(ui_name = 'ui_registration_profile.ui')

from __code.registration.registration import RegistrationFileSelection
from __code.registration.registration_profile import RegistrationProfileUi
import os

list_files = ["/Users/j35/IPTS/charles/im0000.tif",
             "/Users/j35/IPTS/charles/im0320.tif",
             "/Users/j35/IPTS/charles/im0321.tif",
             "/Users/j35/IPTS/charles/im0322.tif",
             "/Users/j35/IPTS/charles/im0323.tif",
             "/Users/j35/IPTS/charles/im0324.tif",
             "/Users/j35/IPTS/charles/im0325.tif",
             "/Users/j35/IPTS/charles/im0326.tif",
            ]

list_files = ["/Volumes/my_book_thunderbolt_duo/IPTS/IPTS-19921-Charles/02/Im0000.tif",
              "/Volumes/my_book_thunderbolt_duo/IPTS/IPTS-19921-Charles/02/Im0032.tif",
              "/Volumes/my_book_thunderbolt_duo/IPTS/IPTS-19921-Charles/02/Im0033.tif",
              "/Volumes/my_book_thunderbolt_duo/IPTS/IPTS-19921-Charles/02/Im0034.tif",
              "/Volumes/my_book_thunderbolt_duo/IPTS/IPTS-19921-Charles/02/Im0035.tif",
              "/Volumes/my_book_thunderbolt_duo/IPTS/IPTS-19921-Charles/02/Im0036.tif",
              "/Volumes/my_book_thunderbolt_duo/IPTS/IPTS-19921-Charles/02/Im0037.tif",
             ]

import glob
list_files = glob.glob("/Volumes/my_book_thunderbolt_duo/IPTS/IPTS-19921-Charles/registration_test_set/*.tif")

[os.path.exists(_file) for _file in list_files]

# + run_control={"frozen": false, "read_only": false}
o_regi = RegistrationFileSelection()
o_regi.load_files(list_files)

# + run_control={"frozen": false, "read_only": false}
o_gui = RegistrationProfileUi(data_dict=o_regi.data_dict['sample'])
o_gui.show()

# + run_control={"frozen": false, "read_only": false}

