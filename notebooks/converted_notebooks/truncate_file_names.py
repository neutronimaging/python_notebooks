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

# + [markdown] run_control={"frozen": false, "read_only": false}
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/tutorials/imaging-notebooks/truncate_file_names/)

# + [markdown] run_control={"frozen": false, "read_only": false}
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code.truncate_file_names.truncate_file_names import TruncateFileNames
from __code import system
system.System.select_working_dir(notebook='truncate_file_names')
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select list of files to rename

# + run_control={"frozen": false, "read_only": false}
o_format = TruncateFileNames(working_dir=system.System.get_working_dir())
o_format.select_input_files()
# -

# # Define part of file to truncate

o_format.define_truncate_part()

# # Checking new names

o_format.o_schema.check_new_names()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select output folder

# + run_control={"frozen": false, "read_only": false}
o_format.o_schema.select_export_folder()
# -

# # Rename the files 

o_format.o_schema.rename_and_export_files()


