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
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/registration/)

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
from __code.registration import RegistrationFileSelection, RegistrationUi

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

# + run_control={"frozen": false, "read_only": false}

