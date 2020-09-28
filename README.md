# Python Notebooks
This reporsitory provides various notebooks for users of the neutron imaging beamlines at ORNL. 
Full tutorial of most of the notebooks can be found at [here](https://neutronimaging.pages.ornl.gov/tutorial/).


## Instructions

The majority of the notebooks are ready to use on the ORNL cluster ([analysis cluster](https://analysis.ornl.gov)) when logged in with your __XCAME__ account.
For those who wish to run these notebooks locally for
* light-weight data processing
* training and education
* development

__two methods__ are provided here to setup your personal environment to run these notebooks.

### Build Local Conda Environment

For most developers who wish to build on top of existing notebooks, it is recommended to build you own local environment such that additional dependencies and modules can be added to the `conda` env easily.
Here are the steps needed to build your own Conda env

* Install `Anaconda3` or `miniconda3`.
  > If one of the two is already installed, skip this step.
* 

### Use pre-configured Docker image


## How to contribute back


## Instructions ##
After bringing the entire project to your computer, create a conda environment (named **notebook_environment** here)
```
conda create -n notebook_environment python=3.6
```

Activate the environment
```
conda activate notebook_environment
```

Then run the following script to install all the necessary libraries
```
./script_for_installation.sh
```

## for developpers ##

Before pushing any changes you made, clean up the notebook by running the command
```
 $ python before_and_after_github_script.py -b
```

and before pushing to repository
```  
$ python before_and_after_github_script.py -a
```

This will reset all the notebooks (clear output) and will allow github to clearly see the differences between notebooks
that have been modified.

To turn debugging mode on, add the flag -d (--use_debugging_mode) to the command

```
$ python before_and_after_github_script.py -a -d
```
