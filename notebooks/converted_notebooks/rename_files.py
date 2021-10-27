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

# + [markdown] run_control={"frozen": false, "read_only": false}
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/rename_files/)

# + [markdown] run_control={"frozen": false, "read_only": false}
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code.rename_files.rename_files import NamingSchemaDefinition, FormatFileNameIndex
from __code import system
system.System.select_working_dir()
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select input folder and define new naming schema

# + run_control={"frozen": false, "read_only": false}
o_format = FormatFileNameIndex(working_dir=system.System.get_working_dir())
o_format.select_input_folder()
# -

# # Checking new names

o_format.o_schema.check_new_names()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select output folder

# + run_control={"frozen": false, "read_only": false}
o_format.o_schema.select_export_folder()
# -


