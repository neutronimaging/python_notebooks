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
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/bragg_edge)
#
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code import system
from __code.bragg_edge.bragg_edge import BraggEdge, Interface

system.System.select_working_dir(facility='SNS', instrument='SNAP')
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Time Spectra File

# + run_control={"frozen": false, "read_only": false}
o_bragg = BraggEdge(working_dir=system.System.get_working_dir())
o_bragg.select_just_time_spectra_file()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Define Experiment Setup

# + run_control={"frozen": false, "read_only": false}
o_bragg.exp_setup()

# + [markdown] run_control={"frozen": false, "read_only": false}
# ## Display Bragg Edges vs Signal

# + run_control={"frozen": false, "read_only": false}
o_bragg.load_time_spectra()
#o_bragg.calculate_counts_vs_file_index_of_regions_selected(list_roi=o_interface.list_roi)
# -

o_bragg.lambda_array

o_bragg.tof_array





# + run_control={"frozen": false, "read_only": false}
from plotly.offline import plot, init_notebook_mode, iplot
init_notebook_mode()
import plotly.plotly as py
import plotly.graph_objs as go
from plotly import tools
from ipywidgets.widgets import interact
from ipywidgets import widgets

# -



# + run_control={"frozen": false, "read_only": false}
bragg_edges = o_bragg.bragg_edges
hkl = o_bragg.hkl
lambda_array = o_bragg.lambda_array
sum_cropped_data = o_bragg.final_image

# format hkl labels
_hkl_formated = {}
for _material in hkl:
    _hkl_string = []
    for _hkl in hkl[_material]:
        _hkl_s = ",".join(str(x) for x in _hkl)
        _hkl_s = _material + "\n" + _hkl_s
        _hkl_string.append(_hkl_s)
    _hkl_formated[_material] = _hkl_string
    
trace = go.Scatter(
    x = o_bragg.lambda_array,
    y = o_bragg.counts_vs_file_index,
    mode = 'markers')

layout = go.Layout(
    width = "100%",
    height = 500,
    title = "Sum Counts vs TOF",
    xaxis = dict(
        title = "Lambda (Angstroms)"
                ),
    yaxis = dict(
        title = "Sum Counts"
                ),
    )

max_x = 6
y_off = 1

for y_index, _material in enumerate(bragg_edges):
    for _index, _value in enumerate(bragg_edges[_material]):
        if _value > max_x:
            continue
        bragg_line = {"type": "line",
                    'x0': _value,
                    'x1': _value,
                     'yref': "paper",
                     'y0': 0,
                     'y1': 1,
                     'line': {
                        'color': 'rgb(255, 0, 0)',
                        'width': 1
            }}
        layout.shapes.append(bragg_line)
        y_off = 1 - 0.25 * y_index
    
        # add labels to plots
        _annot = dict(
                    x=_value,
                    y= y_off,
                    text = _hkl_formated[_material][_index],
                    yref="paper",
                    font=dict(
                        family="Arial",
                        size=16,
                        color="rgb(150,50,50)"
                    ),
                    showarrow=True,
                    arrowhead=3,
                    ax=0,
                    ay=-25)
                
        layout.annotations.append(_annot)
        
data = [trace]

figure = go.Figure(data=data, layout=layout)
iplot(figure)

# -


