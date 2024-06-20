# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
import os
import json
import numpy as np

import matplotlib.pyplot as plt
# %matplotlib notebook
# -

# json file created by GUI from bragg_edge_fitting.ipynb notebook
json_file = "/Users/j35/Desktop/march_dollase_data.json"
assert os.path.exists(json_file)

with open(json_file) as f:
  data = json.load(f)

# +
x_axis = data['xaxis']
y_axis = data['yaxis']
parameters = data['parameters']

x_axis = np.array(x_axis)
y_axis = np.array(y_axis)
# -

parameters


fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(x_axis, y_axis, '.')
plt.show()


