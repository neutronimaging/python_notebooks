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

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS

# + run_control={"frozen": false, "read_only": false}
import warnings
warnings.filterwarnings('ignore')

from __code.ui_builder import UiBuilder
o_builder = UiBuilder(ui_name = 'ui_panoramic_stitching.ui')

from __code.panoramic_stitching import Interface, InterfaceHandler

from __code import system
system.System.select_working_dir()
from __code.__all import custom_style
custom_style.style()

# + run_control={"frozen": false, "read_only": false}
# %gui qt

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Description 

# + [markdown] run_control={"frozen": false, "read_only": false}
# This is just a template notebook for more complex UI that required pyqtgraph

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Images

# + run_control={"frozen": false, "read_only": false}
o_template = InterfaceHandler(working_dir=system.System.get_working_dir())
o_template.select_images(instruction='Select tiff or Fits Images ...')

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Display Images

# + run_control={"frozen": false, "read_only": false}
o_template.load()
o_interface = Interface(o_norm=o_template.o_norm)
o_interface.show()

# + run_control={"frozen": false, "read_only": false}

