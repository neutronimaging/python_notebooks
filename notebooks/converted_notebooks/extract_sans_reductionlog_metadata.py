# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.15.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/extract_sans_reductionlog_metadata)
#
# <img src='__docs/__all/notebook_rules.png' />

# # Select Instrument

# +
from __code.sans import extract
from __code.__all import custom_style
custom_style.style()

initializer = extract.Initializer()
initializer.select_instrument()
# -

# # Select your ReductionLog files and then the Metadata to extract 

working_dir = initializer.get_working_dir()
o_extract = extract.Extract(working_dir=working_dir,
                           instrument=initializer.get_instrument())
o_extract.select_reductionlog()

# # Select output folder

o_extract.export()


