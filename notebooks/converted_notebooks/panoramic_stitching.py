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

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/panoramic_stitching)
#
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS

# + run_control={"frozen": false, "read_only": false}
import warnings
warnings.filterwarnings('ignore')

from __code.ui_builder import UiBuilder
o_builder = UiBuilder(ui_name = 'ui_panoramic_stitching.ui')

from __code.panoramic_stitching import Interface, InterfaceHandler

from __code import system
system.System.select_working_dir()
from __code.__all import custom_style
custom_style.style()

# + run_control={"frozen": false, "read_only": false}
# %gui qt

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Images

# + run_control={"frozen": false, "read_only": false}
o_template = InterfaceHandler(working_dir=system.System.get_working_dir())
o_template.select_images(instruction='Select tiff or Fits Images ...')

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Display Images

# + run_control={"frozen": false, "read_only": false}
o_template.load()
o_interface = Interface(o_norm=o_template.o_norm)
o_interface.show()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # FOR DEBUGGING

# +
from __code.ui_builder import UiBuilder
o_builder = UiBuilder(ui_name = 'ui_panoramic_stitching.ui')

import glob
from NeuNorm.normalization import Normalization
from __code.panoramic_stitching import Interface, InterfaceHandler

#IPTS_folder = '/Volumes/my_book_thunderbolt_duo/IPTS/IPTS-21632-Ed-Jeff-Katie/'
IPTS_folder = '/Users/j35/IPTS/IPTS-21632/'

list_of_images = glob.glob(IPTS_folder + "4_images_to_stitch/*.tiff")
list_of_images.sort()
list_of_images = list_of_images[0:2]
configuration = IPTS_folder + 'roi.txt'
o_norm = Normalization()
o_norm.load(file=list_of_images, notebook=True)

from __code import system
# system.System.select_working_dir()

o_template = InterfaceHandler()
o_template.o_norm = o_norm
# -

# %gui qt

o_interface = Interface(o_norm=o_template.o_norm, configuration=configuration)
o_interface.show()





# %matplotlib notebook
import matplotlib.pyplot as plt
import numpy as np

debug_ref = o_interface.debug_big_array_roi_ref
debug_target = o_interface.debug_big_array_roi_target

# +
fig, (ax1, ax2) = plt.subplots(1, 2)

ax1.imshow(debug_ref)
ax2.imshow(debug_target)

# -



data_reference = o_interface.list_reference['data'][0]
ref_x0 = 1719; ref_y0=147; ref_width=196; ref_height=239
data_reference_of_roi = data_reference[ref_y0:ref_y0+ref_height, ref_x0:ref_x0+ref_width]

fig = plt.figure(2)
ax = plt.imshow(data_reference_of_roi)
plt.colorbar(ax)


