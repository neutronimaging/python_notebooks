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
# # TEST - DEBUG VERSION - NOT TO BE RUN BY USERS!!!!!!

# + [markdown] run_control={"frozen": false, "read_only": false}
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/en/tutorial/notebooks/metadata_overlapping_images/)

# + [markdown] run_control={"frozen": false, "read_only": false}
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # DEBUG

# + run_control={"frozen": false, "read_only": false}
from __code.ui_builder import UiBuilder
o_builder = UiBuilder(ui_name = 'ui_metadata_overlapping_images.ui')
o_builder = UiBuilder(ui_name = 'ui_metadata_overlapping_images_string_format.ui')

from __code import system
from __code.fileselector import FileSelection
from __code.metadata_overlapping_images import MetadataOverlappingImagesUi

# + run_control={"frozen": false, "read_only": false}
# %gui qt

# + run_control={"frozen": false, "read_only": false}
import glob
import os
file_dir = '/Volumes/my_book_thunderbolt_duo/IPTS/IPTS-20139-Hao-Liu/05-07-18_LFR_normalized_light_version/' #MacPro
#file_dir = '/Users/j35/IPTS/charles/data/'

list_files = glob.glob(file_dir + '*.tif') 

o_selection = FileSelection()
o_selection.load_files(list_files)

o_profile = MetadataOverlappingImagesUi(working_dir=os.path.dirname(list_files[0]),
                      data_dict=o_selection.data_dict['sample'])
o_profile.show()

# + run_control={"frozen": false, "read_only": false}


# + run_control={"frozen": false, "read_only": false}

