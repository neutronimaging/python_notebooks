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

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/metadata_ascii_parser/)
#
# <img src='__docs/__all/notebook_rules.png' />

# # Select your IPTS

# +
from __code.metadata_ascii_parser import *

from __code import system
system.System.select_working_dir()
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select the metadata file
# -

o_file = MetadataAsciiParser(system.System.get_working_dir())
o_file.select_metadata_file()

# # Select Metadata Info to Keep 

# + [markdown] run_control={"frozen": false, "read_only": false}
# **Allow users to define:**
#
#  * reference_line_showing_end_of_metadata
#  * start_of_data_after_how_many_lines_from_reference_line
#  * index or label of time info column in big table

# + run_control={"frozen": false, "read_only": false}
o_meta = MetadataFileParser(filename=o_file.metadata_file, 
                            meta_type='mpt',
                            time_label='time/s',
                            reference_line_showing_end_of_metadata='Number of loops',
                            end_of_metadata_after_how_many_lines_from_reference_line=1)
o_meta.parse()

o_meta.select_data_to_keep()
# -

# # Select Output Folder and Filename of new Formated Metadata File

o_meta.keep_only_columns_of_data_of_interest()
o_meta.select_output_location()


