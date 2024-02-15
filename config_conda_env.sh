#!/bin/bash

# update base conda
conda update -y -n base -c defaults conda

# install dependencies from main channel
conda install -c conda-forge nodejs=15.14.0

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
    qtpy              \
    pyqtgraph         \
    inflect           \
    astropy

# install dependencies from conda-forge
conda install -y -c conda-forge \
    ipywe \
    lmfit 

conda install -c conda-forge nbstripout

conda install -c oncat pyoncat

# install additional from pip
pip install \
    chardet \
    h5py \
    algotom \
    neutronbraggedge \
    NeuNorm \
    sectorizedradialprofile \
    ImagingReso \
    ipywidgets \
    changepy \
    tqdm \
    werkzeug=2.0.1


# build Jupyter lab
jupyter labextension install @jupyter-widgets/jupyterlab-manager
jupyter nbextension enable --py widgetsnbextension
jupyter lab build
