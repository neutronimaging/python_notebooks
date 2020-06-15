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

# + run_control={"frozen": false, "read_only": false}
from __code.ui_builder import UiBuilder
o_builder = UiBuilder(ui_name = 'ui_radial_profile.ui')

from __code import system
from __code.fileselector import FileSelection
from __code.radial_profile import RadialProfile, SelectRadialParameters

# system.System.select_working_dir()
# from __code.__all import custom_style
# custom_style.style()

# + run_control={"frozen": false, "read_only": false}
# %gui qt

# + run_control={"frozen": false, "read_only": false}
import glob
import os

file_dir = '/Volumes/my_book_thunderbolt_duo/IPTS/IPTS-19621-CLOCK/CT/'
list_files = glob.glob(file_dir + '*.tiff')

o_selection = FileSelection()
o_selection.load_files(list_files)

o_select = SelectRadialParameters(working_dir=file_dir, 
                                  data_dict=o_selection.data_dict['sample'])
o_select.show()
# -


