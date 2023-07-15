# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.6
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/tutorials/imaging-notebooks/rotate-and-crop-images/)
#
# <img src='__docs/__all/notebook_rules.png' />

# # Select Your IPTS

# +
import warnings
warnings.filterwarnings('ignore')

from __code.load_images import LoadImages
from __code.rotate_and_crop_images.rotate_and_crop_images import RotateAndCropImages, Export

from __code import system
system.System.select_working_dir(notebook='rotate_and_crop_images')
from __code.__all import custom_style
custom_style.style()

# + run_control={"frozen": false, "read_only": false}
# %gui qt

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select and Load Working Images

# + [markdown] run_control={"frozen": false, "read_only": false}
# Select the images (tiff or fits) you want to crop and/or rotate

# + run_control={"frozen": false, "read_only": false}
o_load = LoadImages(working_dir=system.System.get_working_dir())
o_load.select_images(use_next=True)

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select crop region and/or rotation angle 

# + run_control={"frozen": false, "read_only": false}
list_images = o_load.list_images

o_crop = RotateAndCropImages(o_load = o_load)
o_crop.show()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Export Images 

# + run_control={"frozen": false, "read_only": false}
rotated_working_data = o_crop.rotated_working_data
rotation_angle = o_crop.rotation_angle

o_output_folder = Export(working_dir=system.System.get_working_dir(),
                        data=rotated_working_data,
                        list_files=list_images,
                        rotation_angle=rotation_angle)
o_output_folder.select_folder()

# + [markdown] run_control={"frozen": false, "read_only": false}
# Cleaning notebook memory

# + run_control={"frozen": false, "read_only": false}
try:
    del o_crop
    del o_load
except:
    pass
# -


