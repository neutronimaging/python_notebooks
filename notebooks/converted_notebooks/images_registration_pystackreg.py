# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/tutorials/imaging-notebooks/registration/images-registration-using-pystackreg-python-library/)
#
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code.images_registration_pystackreg.main import ImagesRegistrationPystackreg

from __code import system
system.System.select_working_dir(notebook='images_registration_pystackreg')
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select images to register

# + run_control={"frozen": false, "read_only": false}
o_register = ImagesRegistrationPystackreg(working_dir = system.System.get_working_dir())
o_register.select_folder()
# -

# # Display unregistered images 

o_register.display_unregistered()

# # Crop images 

# Select region of images to keep

# %matplotlib widget
o_register.crop_unregistered_images()

o_register.perform_cropping()

# # Define registration parameters 

o_register.define_parameters()

# # Perform registration 

o_register.run()

# # Crop Images

# Select region of images you want to export next

# %matplotlib widget
o_register.crop_registered_images()

# Perform the cropping

o_register.perform_cropping_for_export()

# # Export Images 

o_register.export()
