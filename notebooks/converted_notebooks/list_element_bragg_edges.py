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
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/tutorials/imaging-notebooks/list-element-bragg-edges/)
#
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Import code

# + run_control={"frozen": false, "read_only": false}
from __code.bragg_edge.bragg_edge import BraggEdge, Interface
from __code.__all import custom_style
from __code import system
system.System.log_use(notebook='list_element_bragg_edges')
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Element

# + run_control={"frozen": false, "read_only": false}
o_bragg = BraggEdge()
o_bragg.full_list_elements()
# -

# ## List Bragg Edges 

o_bragg.list_powder_bragg_edges()

# ## Export Table as CSV 

o_bragg.select_output_folder()


