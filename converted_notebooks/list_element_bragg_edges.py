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

# + [markdown] run_control={"frozen": false, "read_only": false}
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/list_element_bragg_edges)
#
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Import code

# + run_control={"frozen": false, "read_only": false}
from __code.bragg_edge.bragg_edge import BraggEdge, Interface
from __code.__all import custom_style
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


