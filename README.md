# Python Notebooks [![DOI](https://zenodo.org/badge/99945953.svg)](https://zenodo.org/badge/latestdoi/99945953)





This repository provides various notebooks for users of the neutron imaging beamlines at ORNL.
Full tutorial of most of the notebooks can be found at [here](https://neutronimaging.pages.ornl.gov/tutorial/).

## Prerequisites

This project uses [Pixi](https://pixi.sh/) for environment and dependency management. Install Pixi:

```bash
curl -fsSL https://pixi.sh/install.sh | bash
```

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/ornlneutronimaging/python_notebooks.git
cd python_notebooks_development
```

2. Install dependencies:
```bash
pixi install
```

3. Launch Jupyter Lab:
```bash
pixi run lab
```

## Available Commands

- `pixi run lab` - Start Jupyter Lab
- `pixi run notebook` - Start Jupyter Notebook  
- `pixi run test` - Run tests
- `pixi run test_imports` - Verify all packages import correctly
- `pixi run test_all` - Run all tests
- `pixi run check` - Run installation check

For development:
- `pixi run -e dev lint` - Run code linting

## Instructions

To learn more about the notebooks and how to use them, refer to the complete tutorial found on our imaging web site https://neutronimaging.pages.ornl.gov

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


<!-- ## for developers ##

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

To run the tests:
```bash
pixi run test
# or
pixi run test_all  # runs all test suites
```
## Deployment

This project uses Pixi for reproducible environments. The `pixi.lock` file ensures consistent dependencies across all installations.

### Environment Management

- Default environment: `pixi shell` or `pixi run <command>`
- Development environment: `pixi run -e dev <command>`

Notebooks are distributed directly by the Computational Instrument Scientist.
