# Python Notebooks [![Build Status](https://www.travis-ci.com/neutronimaging/python_notebooks.svg?branch=master)](https://www.travis-ci.com/neutronimaging/python_notebooks) [![DOI](https://zenodo.org/badge/99945953.svg)](https://zenodo.org/badge/latestdoi/99945953)





This reporsitory provides various notebooks for users of the neutron imaging beamlines at ORNL. 
Full tutorial of most of the notebooks can be found at [here](https://neutronimaging.pages.ornl.gov/tutorial/).

## Instructions

To learn how to access or install the notebooks, and how to run them, refer to the complete tutorial found on our imaging web site https://neutronimaging.pages.ornl.gov

![Screen Shot 2021-06-11 at 8 03 33 AM](https://user-images.githubusercontent.com/1138324/121683900-000cc080-ca8c-11eb-815f-5ff52731dba7.png)

## Instrument References
For more information about the facility and instruments, navigate to the following links:
- [ORNL Neutron Imaging Website](https://neutronimaging.ornl.gov/)
- [Multimodal Advanced Radiography Station (MARS)](https://neutrons.ornl.gov/mars)
- [Versatile Neutron Imaging Instrument (VENUS)](https://neutrons.ornl.gov/venus)


## How to contribute back

You can contribute back to this repo by 
* fork it to your own account
* make the necessary adjustments
* make a pull request on Github.

The maintainer of this repo will review your changes and provided feedback if needed.
A more detailed instructions can be found in this [post by DataSchool](https://www.dataschool.io/how-to-contribute-on-github/).


<!-- ## for developpers ##

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
``` -->

To run the tests
```
$ cd notebooks
$ export PYTHONPATH=$PWD:$PYTHONPATH
$ pytest
```
## Deployment

An updated deployment strategy is underway.

Currently, notebooks are distributed directly by the Computational Instrument Scientist.
