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

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/mcp_chips_corrector)
#
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
import warnings
warnings.filterwarnings('ignore')

from __code import system
from __code.mcp_chips_corrector.mcp_chips_corrector import McpChipsCorrector
from __code.mcp_chips_corrector.interface import Interface
system.System.select_working_dir()
from __code.__all import custom_style
custom_style.style()
# -

# ## UI Setup 

# %gui qt

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select MCP data corrected folder

# + run_control={"frozen": false, "read_only": false}
o_corrector = McpChipsCorrector(working_dir = system.System.get_working_dir())
o_corrector.select_folder()
# -

# # Launch UI 

o_interface = Interface(o_corrector=o_corrector)
o_interface.show()
