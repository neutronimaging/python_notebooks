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

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/tutorials/imaging-notebooks/extract/extract-nexus-daslogs/)
#
# <img src='__docs/__all/notebook_rules.png' />

# # Select your IPTS 

# +
from __code.extract_nexus_daslogs import extract

from __code import system
system.System.select_working_dir(notebook='extract_nexus_daslogs')
from __code.__all import custom_style
custom_style.style()
# -

# # Select list of NeXus to extract metadata from

o_extract = extract.Extract(working_dir=system.System.get_working_dir())
o_extract.select_nexus()

o_extract.export()


