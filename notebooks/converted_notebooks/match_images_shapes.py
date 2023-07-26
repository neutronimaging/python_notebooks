# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.7
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/tutorials/imaging-notebooks/match-images-shapes/)
#
# <img src='__docs/__all/notebook_rules.png' />

# # Select Your IPTS

# +
from __code.match_images_shapes.load_images import LoadImages
from __code.match_images_shapes.main import Main

from __code import system
system.System.select_working_dir(notebook='math_images_shapes')
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select and Load Working Images

# + [markdown] run_control={"frozen": false, "read_only": false}
# Select the images (tiff or fits) you want to work with

# + run_control={"frozen": false, "read_only": false}
o_load = LoadImages(working_dir=system.System.get_working_dir())
o_load.select_images(use_next=True)
# -

# # Shapes available 

o_main = Main(working_data=o_load.working_data, list_images=o_load.list_images, working_metadata=o_load.working_metadata)
o_main.display_available_shapes()

# # Select output location 

o_main.select_output_folder()


