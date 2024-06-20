# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/cylindrical-geometry-correction-with-embedded-widgets/)
#
# <img src='__docs/__all/notebook_rules.png' />

# # Workflow of the notebook 

# * **User**: select the images to work with.
# * *Notebook*: load images
# * *OPTIONAL*: **User** load config file
# * **User**: rotate the images to make sure the sample to work with is perfectly vertical
# * **User**: select region to work with by cropping the raw data
# * *OPTIONAL*: **User** export the cropped images
# * **User**: select part of the image that does not contain the sample
# * **User**: select part of the image that does contain the sample
# * *Notebook*: remove background from sample part
# * *Notebook*: display profiles
# * *Notebook*: apply geometry correction to all profiles
# * **User**: select where to output the images corrected, profiles ascii files, metadata file, and config file.

# # Select your IPTS

# +
# %matplotlib notebook

import warnings
warnings.filterwarnings('ignore')

from __code.cylindrical_geometry_correction_embedded_widgets.main import CylindricalGeometryCorrectionEmbeddedWidgets

from __code import system
system.System.select_working_dir(notebook='cylindrical_geometry_correction_embedded_widgets')

from __code.__all import custom_style
custom_style.style()
# -

# # Select Images 

o_ipts = CylindricalGeometryCorrectionEmbeddedWidgets(working_dir=system.System.get_working_dir())
o_ipts.select_images()

# # Use config file (optional)
#
# Run this cell when you have a config file you saved in a previous session and wants to reload it here. This will allow you to automatically re-use the same region of interests. 

o_ipts.select_config()

# # Visualize Raw Data

o_ipts.visualize_raw_images()

# # Rotate sample to make sure it's perfectly vertical
#
# Use the **vertical guide** to help you find the perfect vertical to your sample.
#
# <img src='__code/cylindrical_geometry_correction_embedded_widgets/static/example_of_bad_and_good_alignments.png' />
#
# Feel free to use the **green** and **blue** horizontal profiles helper to make sure the sample is perfectly vertical. To do so, place one of the two profile helper near the top of the sampel and the other one, near the bottom and make sure the edge is perfectly aligned top to bottom.
#
# <img src='__code/cylindrical_geometry_correction_embedded_widgets/static/example_rotation_guides.png' />

o_ipts.rotate_images()

# # crop sample to region of interest 

# By playing with the **left**, **right**, **top** and **bottom** sliders, select a region surrounding the data you want to work with.
#
# Use the **profile marker** to make sure the crop region is tight around the sample.
#
# <html>
#     <br>
#     <font color="red">Warning:</color>
#     </html>
#
# * Make sure you include the container in the selection (edges should have a value of 1)
# and 
# * a part of the container without sample inside (will be used for normalization)
#
# For example:
#
# <img src='__code/cylindrical_geometry_correction_embedded_widgets/static/example_crop_region.png' />

o_ipts.apply_rotation()
o_ipts.select_crop_region()

# ## Export cropped images (optional)

o_ipts.export_cropped_images()

# # Select background
#
# Select a part of the tube that does not contain the sample. The horizontal profile of this region, integrated over the y-axis, will be used as the background signal to remove from the data.
#
# __for example:__
#
# <img src='__code/cylindrical_geometry_correction_embedded_widgets/static/example_background_selection.png' />

o_ipts.background_range_selection()

# # Select sample
#
# Select the **top** and **bottom** limit of your sample. 
#
# __For example:__
#
# <img src='__code/cylindrical_geometry_correction_embedded_widgets/static/example_of_sample_selection.png' />
#

o_ipts.sample_region_selection()

# # Removing tube background from sample

o_ipts.remove_background_signal()

# # Profiles to work with 

o_ipts.display_of_profiles()

# # Applying geometry correction 

o_ipts.correct_cylinder_geometry()

# # Export 
#
# This will export:
#  - the corrected cropped images
#  - the full horizontal profiles of each image
#  - all the configuration used in this notebook (config file)

o_ipts.export_profiles()


