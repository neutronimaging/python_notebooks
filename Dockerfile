FROM jupyter/scipy-notebook:latest
LABEL version="0.0.1" \
      maintainer="KedoKudo <zhangc@ornl.gov>" \
      lastupdate="2020-09-28"
USER  root
EXPOSE 8888

ENV PYONCAT_LOCATION="https://oncat.ornl.gov/packages/pyoncat-1.4.1-py3-none-any.whl"

# Since we are using Jupyter official image, the 
# majority of the dependencies are already resolved
RUN conda install --quiet --yes \
    requests          \
    requests-oauthlib \
    plotly            \
    nodejs            \
    qtpy              \
    pyqtgraph         \
    astropy           \
    && \
    conda install -c conda-forge --quiet --yes \
    ipywe \
    lmfit \
    && \
    conda clean --all --yes \
    && \
    pip install \
    neutronbraggedge \
    NeuNorm \
    sectorizedradialprofile \
    $PYONCAT_LOCATION \
    && \
    conda clean --all --yes \
    && \
    npm cache clean --force

# Directly inherit the CMD from the base image
# 
# 
# -- USER INSTRUCTION --
# Use the following command to start the notebook
# $ docker run --rm -p 38764:8888 -e JUPYTER_ENABLE_LAB=yes -v "$PWD":/home/jovyan/work kedokudo/neutron-imaging:latest
# then use the link in the command prompt to connect to Jupyter
# > NOTE: you need to replace 127.0.0.1 to localhost in the URL
#
# 
# -- DEVELOPER INSTRUCTION --
# User the following command to build the image
# $ docker build -t YOUR_DOCKERHUB_ID/NAME_OF_THIS_IMAGE:VERSION
# 