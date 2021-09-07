# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code.display_and_export_images_with_metadata_profile import DisplayExportScreenshots
from __code import system
system.System.select_working_dir()
from __code.__all import custom_style
custom_style.style() 

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Description 

# + [markdown] run_control={"frozen": false, "read_only": false}
# This notebook will display (and save) the images with the metadata profile calculated in the [file_name_and_metadata_vs_time_stamp](file_name_and_metadata_vs_time_stamp.ipynb).
#
# Then you will also have the option to export all the images and metadata profile plots.

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Image Folder 
# -

o_display_export = DisplayExportScreenshots(working_dir=system.System.get_working_dir())
o_display_export.select_input_folder()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select File Name vs Metatdata ASCII file

# + [markdown] run_control={"frozen": false, "read_only": false}
# This file should have been created by [file_name_and_metadata_vs_time_stamp](file_name_and_metadata_vs_time_stamp.ipynb)
# -

o_display_export.select_metadata_file()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Display Images with Profile of metadata 

# + run_control={"frozen": false, "read_only": false}
o_display_export.display()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Output all screenshots

# + run_control={"frozen": false, "marked": false, "read_only": false}
o_display_export.select_export_folder()

# + run_control={"frozen": false, "read_only": false}
o_display_export.export()

# + run_control={"frozen": false, "read_only": false}

