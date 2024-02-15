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

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/tutorials/imaging-notebooks/display/display-and-export-images-with-timestamps/)
#
# <img src='__docs/__all/notebook_rules.png' />

# # Select your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code import system
system.System.select_working_dir(notebook='display_and_export_images_with_timestamp')
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Description 

# + [markdown] run_control={"frozen": false, "read_only": false}
# This notebook will display (and save) the images with the **absolute** or **relative** time stamp.
#
# Then you will also have the option to export all the images to create for example a movie out of it.

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Python Import 

# + run_control={"frozen": false, "read_only": false}
from __code.display_and_export_images_with_time_stamp import DisplayExportScreenshots

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Image Folder 

# + run_control={"frozen": false, "read_only": false}
working_dir = system.System.get_working_dir()
o_file_time_stamp = DisplayExportScreenshots(working_dir=working_dir)
o_file_time_stamp.select_image_folder()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Retrieve Time Stamp

# + run_control={"frozen": false, "read_only": false}
o_file_time_stamp.retrieve_time_stamp()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Display images with Relative Time Info

# + run_control={"frozen": false, "read_only": false}
o_file_time_stamp.load()

# + run_control={"frozen": false, "read_only": false}
o_file_time_stamp.preview()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Export Stack of Images

# + run_control={"frozen": false, "read_only": false}
o_file_time_stamp.select_export_folder()

# + run_control={"frozen": false, "read_only": false}
o_file_time_stamp.export()
# -


