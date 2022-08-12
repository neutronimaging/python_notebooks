# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# + run_control={"frozen": false, "read_only": false}
debugging = True
IPTS = 19558

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Description 

# + [markdown] run_control={"frozen": false, "read_only": false}
# Steps are:
#  - load a stack of images
#  - define your sample
#  
# => the average counts of the region vs the stack (index, TOF or lambda) will be displayed
# compared to the theory signal of a given set of layers.

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Notebook Initialization 

# + run_control={"frozen": false, "read_only": false}
from __code.__all import custom_style
custom_style.style()

# + run_control={"frozen": false, "read_only": false}
# %gui qt

# + run_control={"frozen": false, "marked": true, "read_only": false}
from __code.ui_builder import UiBuilder
o_builder = UiBuilder(ui_name = 'ui_resonance_imaging_experiment_vs_theory.ui')
o_builder = UiBuilder(ui_name = 'ui_resonance_imaging_layers_input.ui')

from __code import file_handler, utilities
from __code.display_counts_of_region_vs_stack_vs_theory import ImageWindow
from __code.display_imaging_resonance_sample_definition import SampleWindow
from NeuNorm.normalization import Normalization
from __code.ipywe import fileselector

import pprint

if debugging:
    ipts = IPTS
else:
    ipts = utilities.get_ipts()
working_dir = utilities.get_working_dir(ipts=ipts, debugging=debugging)
print("Working dir: {}".format(working_dir))

# + [markdown] cell_style="split" run_control={"frozen": false, "read_only": false}
# # Select Stack Folder

# + format="tab" run_control={"frozen": false, "read_only": false}
input_folder_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select Input Folder',
                                                       type='directory', 
                                                       start_dir=working_dir, 
                                                       multiple=False)
input_folder_ui.show()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Load Stack

# + run_control={"frozen": false, "read_only": false}
working_folder = input_folder_ui.selected
o_norm = Normalization()
o_norm.load(folder=working_folder, notebook=True)

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Define Sample 

# + run_control={"frozen": false, "read_only": false}
_sample = SampleWindow(parent=None, debugging=debugging)
_sample.show()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Region and display Counts

# + run_control={"frozen": false, "read_only": false}
o_reso = _sample.o_reso

_image = ImageWindow(
    stack=(o_norm.data['sample']['data']), working_folder=working_folder, o_reso=o_reso)
_image.show()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Export 

# + [markdown] run_control={"frozen": false, "read_only": false}
# UNDER CONSTRUCTION!

# + run_control={"frozen": false, "read_only": false}

