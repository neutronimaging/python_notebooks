# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# <img src='../__docs/__all/notebook_rules.png' />

# **Workflow of this notebook**
#
# * **User**: select the images to work with.
# * *Notebook*: load and automatically rotate the data 90 degrees to match the algorithm orientation 
# * **User**: select region to work with by cropping the raw data
# * **User**: select horizontal range of profile to combine
# * *Notebook*: use that range and combine the data using a mean
# * *Notebook*: display the profiles to work with, one profile per image loaded
# * **User**: select the position (edges) of the inner and outer cylinders
# * *Notebook*: clean the edges by removing data outside of the outer cylinder
# * *Notebook*: switch from transmission to attenuation mode
# * *Notebook*: calculate the number of counts per pixel in the outer cylinder
# * *Notebook*: apply geometry correction to all profiles
# * **User**: now working on the inner cylinder, check or redefine the edges of the inner cylinder
# * *Notebook*: apply geometry correction to inner cylinder
# * **User**: select where to output the ascii files that will contains the profiles.

# # Python Import 

# +
import os
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

# %matplotlib notebook

from __code import system
system.System.select_working_dir()

from ipts_28402_code.ipts_28402 import IPTS_28402

# -

# # Select Images 

o_ipts = IPTS_28402(working_dir=system.System.get_working_dir())
o_ipts.select_images()

# # Visualize Raw Data

# The data are rotated 90 degrees to work with the cylindrical geometry algorithm

o_ipts.visualize_raw_images()

# # crop sample to region of interest 

# By playing with the **left**, **right**, **top** and **bottom** sliders, select a region surrounding the data you
# want to correct.
# <html>
#     <br>
#     <font color="red">Warning:</color>
#     </html>
# Make sure you include the external cylinder (container) in the selection.

o_ipts.select_crop_region()

# ## Visualize result of cropping 

o_ipts.visualize_crop()

# # Selection of the profiles to correct
#
# Select the **top limit** and **bottom limit** profiles to correct. The program will integrate vertically all the counts between those two limits.

o_ipts.selection_of_profiles_limit()

# # Profiles to work with 

o_ipts.display_of_profiles()

# # Let's define the position of the cylinders edges 

o_ipts.cylinders_positions()

# # Cleaning edges
#
# Data outside of the cylinders must be removed. To do so, the algorithm will use the **outer_radius** value you defined in the previous cell and will only keep the data within that region.

o_ipts.cleaning_edges()

# # Switching to attenuation mode  

o_ipts.switching_to_attenuation_mode()

# # Calculate number of counts per pixel in outer cylinder.

o_ipts.outer_cylinder_geometry_correction()

# # Applying outer cylinder correction to all profiles

o_ipts.full_profile_with_only_outer_cylinder_corrected()

# # Working on inner cylinder 

# We find the center, radius and truncate outside cylinder, keeping only the data from the inner cylinder
#
# **Instructions**
# In the following plot, make sure the edges you predefined before are still matching the edge of the inner cylinder profile.

o_ipts.crop_to_inner_cylinder()

o_ipts.correct_inner_cylinder_geometry()

# # Export profile(s) corrected into text file(s)
#
# Select the folder where you want to create the text files, comma separated file, of the inner cylinder profiles corrected. Each image will have its own text file.

o_ipts.export_profiles()




