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
# # select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
from __code.file_name_and_metadata_vs_time_stamp import FileNameMetadataTimeStamp

from __code import system
system.System.select_working_dir()
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Description 

# + [markdown] run_control={"frozen": false, "read_only": false}
# The goal of this notebook is __to match__ the **file names** (fits or tif) with their **metadata** (imported from an ascii file)
#
# The program will retrieve the time stamp of the imported file and will match them with the metadata ascii file. 
#
# To work, the metadata will need to have the following format
#
# **furnace.txt**
# ```
# #time, metadata
# 120000, 0
# 120001, 5
# 120010, 10
# 120020, 30
# ```
#
# A preview of the **metadata** value vs **file index** and **relative time** will be displayed. 
#
# Export of the data into an ascii file using the following format
# ```
# #metadata, file_name, time_stamp
# ```
#

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Python Import

# + run_control={"frozen": false, "read_only": false}
# %matplotlib notebook

# + run_control={"frozen": false, "read_only": false}
# from __code.file_name_and_metadata_vs_time_stamp import FileNameMetadataTimeStamp

# + run_control={"frozen": false, "read_only": false}
from __code import utilities
#from __code import utilities, gui_widgets, file_handler
# import ipywe.fileselector
# from IPython.core.display import display, HTML
# import pandas as pd
# import numpy as np
# from pprint import pprint

# from ipywidgets import widgets
# from IPython.core.display import display, HTML            
  
import matplotlib.pyplot as plt
# %matplotlib notebook

# from IPython import display as display_ipython

from plotly.offline import plot, init_notebook_mode, iplot
init_notebook_mode()
import plotly.plotly as py
import plotly.graph_objs as go



# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Image Folder

# + run_control={"frozen": false, "read_only": false}
o_meta_file_time = FileNameMetadataTimeStamp(working_dir=system.System.get_working_dir())
o_meta_file_time.select_image_folder()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Metadata Ascii File 

# + run_control={"frozen": false, "read_only": false}
o_meta_file_time.select_metadata_file()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Format and Merging Data

# + run_control={"frozen": false, "read_only": false}
if my_system == 'mac':
    my_header = [None, "furnace vacuum2", None, "furnace vacuum1", None, "tolerance",
                None, "%power", None, "OT Temp", None, "Ramp SP", None,
                "OT SP", None, "Setpoint", None, "Sample", None]
else:
    my_header = [None, "furnace\ vacuum2", None, "furnace\ vacuum1", None, "tolerance",
                None, "%power", None, "OT\ Temp", None, "Ramp\ SP", None,
                "OT\ SP", None, "Setpoint", None, "Sample", None]

# + run_control={"frozen": false, "read_only": false}
o_meta_file_time.format_files(metadata_header=my_header)
o_meta_file_time.merging_formated_files()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Preview 

# + run_control={"frozen": false, "read_only": false}
o_meta_file_time.preview()

# + run_control={"frozen": false, "read_only": false}
trace = go.Scatter(x=o_meta_file_time.file_index,
                           y=o_meta_file_time.metadata_array,
                           mode='markers',
                           name='Metadata Profile vs File Index')

layout = go.Layout(width="100%",
                   height=500,
                   showlegend=False,
                   title='Profile of Metadata vs File Index',
                   xaxis={'title': 'File Index'},
                   yaxis={'title': 'Metadata Value'},
                   )

data = [trace]
figure = go.Figure(data=data, layout=layout)
iplot(figure)

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Export data 

# + run_control={"frozen": false, "read_only": false}
o_meta_file_time.select_export_folder()

# + run_control={"frozen": false, "read_only": false}
o_meta_file_time.export()
