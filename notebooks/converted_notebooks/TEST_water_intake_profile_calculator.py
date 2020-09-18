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
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/en/tutorial/notebooks/water_intake_profile_calculator/)

# + [markdown] run_control={"frozen": false, "read_only": false}
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code.ui_builder import UiBuilder
o_builder = UiBuilder(ui_name = 'ui_water_intake_profile.ui')
from __code.roi_selection_ui import Interface

from __code import system
from __code.water_intake_profile_calculator import WaterIntakeProfileCalculator, WaterIntakeProfileSelector

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
o_water = WaterIntakeProfileCalculator(working_dir=system.System.get_working_dir())
o_water.select_data()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Profile Region 

# + run_control={"frozen": false, "read_only": false}
o_gui = WaterIntakeProfileSelector(dict_data=o_water.dict_files)
o_gui.show()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # # %DEBUGGING

# + run_control={"frozen": false, "read_only": false}
from __code import system
from __code.water_intake_profile_calculator import WaterIntakeProfileCalculator, WaterIntakeProfileSelector

# + run_control={"frozen": false, "read_only": false}
# %gui qt

# + run_control={"frozen": false, "read_only": false}
list_files = ['/Volumes/my_book_thunderbolt_duo/IPTS/IPTS-Das-Saikat/only_data_of_interest/image_00544.tif',
              '/Volumes/my_book_thunderbolt_duo/IPTS/IPTS-Das-Saikat/only_data_of_interest/image_00545.tif',
              '/Volumes/my_book_thunderbolt_duo/IPTS/IPTS-Das-Saikat/only_data_of_interest/image_00546.tif',
              '/Volumes/my_book_thunderbolt_duo/IPTS/IPTS-Das-Saikat/only_data_of_interest/image_00547.tif',
              '/Volumes/my_book_thunderbolt_duo/IPTS/IPTS-Das-Saikat/only_data_of_interest/image_00548.tif',
             ]

list_files = ['/Volumes/my_book_thunderbolt_duo/IPTS/IPTS-15177/Sample5_uptake_no bad images/Sample5_1min_r_0.tif',
             '/Volumes/my_book_thunderbolt_duo/IPTS/IPTS-15177/Sample5_uptake_no bad images/Sample5_1min_r_1.tif',
             '/Volumes/my_book_thunderbolt_duo/IPTS/IPTS-15177/Sample5_uptake_no bad images/Sample5_1min_r_2.tif',
             '/Volumes/my_book_thunderbolt_duo/IPTS/IPTS-15177/Sample5_uptake_no bad images/Sample5_1min_r_3.tif',
             '/Volumes/my_book_thunderbolt_duo/IPTS/IPTS-15177/Sample5_uptake_no bad images/Sample5_1min_r_4.tif',
             ]

list_files = ["/Users/j35/IPTS/charles/im0000.tif",
             "/Users/j35/IPTS/charles/im0320.tif",
             "/Users/j35/IPTS/charles/im0321.tif",
             "/Users/j35/IPTS/charles/im0322.tif",
             "/Users/j35/IPTS/charles/im0323.tif",
             "/Users/j35/IPTS/charles/im0324.tif",
             "/Users/j35/IPTS/charles/im0325.tif",
             "/Users/j35/IPTS/charles/im0326.tif",
            ]


o_water = WaterIntakeProfileCalculator()
o_water.load_and_plot(list_files)
o_gui = WaterIntakeProfileSelector(dict_data = o_water.dict_files)
o_gui.show()

# + run_control={"frozen": false, "read_only": false}
171-66+131
# -

236*0.05



