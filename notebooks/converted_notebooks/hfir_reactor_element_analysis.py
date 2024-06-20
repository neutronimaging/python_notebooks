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
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/tutorials/imaging-notebooks/hfir-reactor-element-analysis-tool/)

# + [markdown] run_control={"frozen": false, "read_only": false}
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS

# + run_control={"frozen": false, "read_only": false}
import warnings
warnings.filterwarnings('ignore')

from __code.hfir_reactor_element_analysis.hfir_reactor_element_analysis import HfirReactorElementAnalysis
from __code.hfir_reactor_element_analysis.interface_handler import InterfaceHandler

from __code import system
system.System.select_working_dir(notebook='hfir_reactor_element_analysis')
from __code.__all import custom_style
custom_style.style()

# + run_control={"frozen": false, "read_only": false}
# %gui qt

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select ASCII file 
#
# This file should have been created by the [circular_profile_of_a_ring](circular_profile_of_a_ring.ipynb) notebook.

# + run_control={"frozen": false, "read_only": false}
o_selection = HfirReactorElementAnalysis(working_dir=system.System.get_working_dir())
o_selection.select_ascii_file()
# -

o_select = InterfaceHandler(working_dir=system.System.get_working_dir(), 
                            o_selection=o_selection)


# # DEBUG 

# +
from __code.hfir_reactor_element_analysis.hfir_reactor_element_analysis import HfirReactorElementAnalysis
from __code.hfir_reactor_element_analysis.interface_handler import InterfaceHandler
import os

ascii_file_name = '/Users/j35/IPTS/HFIR-Reactor/HFIR-Reactor_profiles_top.csv'
assert os.path.exists(ascii_file_name)
# -

# %gui qt

# +
o_selection = HfirReactorElementAnalysis(working_dir="/Users/j35/IPTS/HFIR-Reactor/")
o_selection.load_ascii(ascii_file_name)

o_select = InterfaceHandler(working_dir="/Users/j35/IPTS/HFIR-Reactor/", 
                            o_selection=o_selection)
# -


