# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# + [markdown] run_control={"frozen": false, "read_only": false}
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/tutorials/imaging-notebooks/combine/combine-images-without-outliers/)
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code import system
from __code.combine_images_without_outliers.combine_images import Interface

system.System.select_working_dir(facility='SNS', instrument='VENUS', notebook='combine_images_without_outliers')
from __code.__all import custom_style
custom_style.style()
# -

# # Select how you want to combine the first images 

o_combine = Interface(working_dir=system.System.get_working_dir())

# # Select output folder 

o_combine.select_output_folder()


