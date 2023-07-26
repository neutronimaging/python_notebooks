# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.7
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# + [markdown] run_control={"frozen": false, "read_only": false}
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.ornl.gov/tutorials/imaging-notebooks/overlay-images/)

# + [markdown] run_control={"frozen": false, "read_only": false}
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS

# + run_control={"frozen": false, "read_only": false}
import warnings
warnings.filterwarnings('ignore')

from __code.overlay_images.interface_handler import InterfaceHandler
from __code.overlay_images.overlay_images import OverlayImages

from __code import system
system.System.select_working_dir(notebook='overlay_images')
from __code.__all import custom_style
custom_style.style()

# + run_control={"frozen": false, "read_only": false}
# %gui qt

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select folder containing high resolution images

# + run_control={"frozen": false, "read_only": false}
o_data = OverlayImages(working_dir=system.System.get_working_dir())
o_data.select_input_folder(data_type='high resolution')
# -

# # Select folder containing low resolution images 

o_data.select_input_folder(data_type='low resolution')

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Launch User Interface

# + run_control={"frozen": false, "read_only": false}
o_interface = InterfaceHandler(o_norm_high_res=o_data.o_norm_high_res,
                               o_norm_low_res=o_data.o_norm_low_res,
                               working_dir=o_data.working_dir)
# -


