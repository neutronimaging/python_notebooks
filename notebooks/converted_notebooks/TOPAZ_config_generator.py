# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.6
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# + [markdown] run_control={"frozen": false, "read_only": false}
# [![Notebook Tutorial](__code/__all/notebook_tutorial.png)](https://neutronimaging.pages.ornl.gov/en/tutorial/notebooks/topaz_config_generator/)

# + [markdown] run_control={"frozen": false, "read_only": false}
# <img src='__docs/__all/notebook_rules.png' />

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Select IPTS

# + run_control={"frozen": false, "marked": true, "read_only": false}
from __code import system
from IPython.core.display import HTML

from __code.topaz_config_generator import TopazConfigGenerator, ConfigLoader
system.System.select_working_dir(system_folder='/SNS/TOPAZ/')

from __code.__all import custom_style
custom_style.style()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Initialize parameters using configuration file

# + [markdown] run_control={"frozen": false, "read_only": false}
# If you want to initialize all the widgets of this notebook with a configuration file you previously created, select the config file here, otherwise, just run the cell without selecting any file.

# + run_control={"frozen": false, "read_only": false}
o_config_loader = ConfigLoader(working_dir=system.System.get_working_dir())
o_config_loader.select_config_file()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Define Parameters 

# + run_control={"frozen": false, "read_only": false}
_cfg = TopazConfigGenerator(working_dir=system.System.get_working_dir(), 
                            config_dict_loaded=o_config_loader.config_dict)

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Export the Config File 

# + run_control={"frozen": false, "read_only": false}
_cfg.create_config()

# + [markdown] run_control={"frozen": false, "read_only": false}
# # Run Reduction 

# + run_control={"frozen": false, "read_only": false}
_cfg.run_reduction()

# + [markdown] run_control={"frozen": false, "read_only": false}
# <img src='__docs/topaz_config_generator/run_reduction_manually.gif' />

# + run_control={"frozen": false, "read_only": false}

