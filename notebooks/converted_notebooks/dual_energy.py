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

# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/tutorial/notebooks/dual_energy)

# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select Your IPTS 

# + run_control={"frozen": false, "read_only": false}
import warnings
warnings.filterwarnings('ignore')

from __code.dual_energy.dual_energy import Interface, DualEnergy

from __code import system
system.System.select_working_dir()
from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # UI setup

# + run_control={"frozen": false, "read_only": false}
# %gui qt

# + [markdown] cell_style="split" run_control={"frozen": false, "read_only": false}
# # Select data input folder

# + run_control={"frozen": false, "read_only": false}
o_dual = DualEnergy(working_dir=system.System.get_working_dir())
o_dual.select_working_folder()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Launch UI

# + run_control={"frozen": false, "read_only": false}
o_interface = Interface(o_dual=o_dual, spectra_file=o_dual.spectra_file)
o_interface.show()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # DEBUGGING 

# +
import warnings
warnings.filterwarnings('ignore')

from __code.dual_energy.dual_energy import Interface, DualEnergy
import glob
import os
# -

# %gui qt

# +
data_path = '/Users/j35/IPTS/VENUS/IPTS-25778_normalized'
list_data = glob.glob(data_path + "*.tif")
spectra_file = os.path.join(data_path, "Image019_Spectra.txt")
assert os.path.exists(spectra_file)

o_dual = DualEnergy(working_dir=data_path)
o_dual.load_data(data_path)
# -

o_interface = Interface(o_dual=o_dual,
                       working_dir=data_path,
                       spectra_file=spectra_file)
o_interface.show()


