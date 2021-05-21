#!/bin/bash

# This is a special package for ORNL
PYONCAT_LOCATION="https://oncat.ornl.gov/packages/pyoncat-1.4.1-py3-none-any.whl"

# update base conda
conda update -y -n base -c defaults conda

# install dependencies from main channel
conda install -y      \
    requests          \
    requests-oauthlib \
    numpy             \
    scipy             \
    pandas            \
    scikit-image      \
    matplotlib        \
    plotly            \
    jupyter           \
    jupyterlab        \
    nodejs            \
    qtpy              \
    pyqtgraph         \
    astropy

# install dependencies from conda-forge
conda install -y -c conda-forge \
    ipywe \
    lmfit 

conda install -c conda-forge nbstripout

# install additional from pip
pip install \
    neutronbraggedge \
    NeuNorm \
    sectorizedradialprofile \
    inflect \
    ImagingReso \
    ipywidgets \
    changepy \
    tqdm \
    $PYONCAT_LOCATION

# build Jupyter lab
jupyter labextension install @jupyter-widgets/jupyterlab-manager
jupyter nbextension enable --py widgetsnbextension
jupyter lab build
