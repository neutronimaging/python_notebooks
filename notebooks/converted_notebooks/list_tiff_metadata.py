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

# + [markdown] run_control={"frozen": false, "read_only": false}
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/tutorials/imaging-notebooks/list-tiff-metadata/)

# + [markdown] run_control={"frozen": false, "read_only": false}
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS

# + run_control={"frozen": false, "read_only": false}
from __code.select_metadata_to_display import DisplayMetadata
from __code import system
system.System.select_working_dir(notebook='list_tiff_metadata')
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select TIFF Images

# + run_control={"frozen": false, "read_only": false}
o_meta = DisplayMetadata(working_dir=system.System.get_working_dir())
o_meta.select_images(instruction='Select TIFF images ...')

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Metadata to Display

# + [markdown] run_control={"frozen": false, "read_only": false}
# Display list of metadata (according to first tiff image)

# + run_control={"frozen": false, "read_only": false}
o_meta.display_metadata_list()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Metadata Selected Displayed for all Files Loaded

# + run_control={"frozen": false, "read_only": false}
o_meta.display_metadata_selected()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Export Metadata Selected 

# + run_control={"frozen": false, "read_only": false}
o_meta.select_output_folder(instruction='Select Output Folder ...')

# + run_control={"frozen": false, "read_only": false}
o_meta.export()

# + run_control={"frozen": false, "read_only": false}

