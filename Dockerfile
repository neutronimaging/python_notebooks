FROM jupyter/scipy-notebook:latest

EXPOSE 8888

ENV JUPYTER_ENABLE_LAB=yes \
    PYONCAT_LOCATION="https://oncat.ornl.gov/packages/pyoncat-1.4.1-py3-none-any.whl" \
    LIBGL_ALWAYS_INDIRECT=1

USER root
RUN echo jovyan ALL=NOPASSWD:ALL > /etc/sudoers.d/jovyan

USER jovyan
COPY ./notebooks/ /home/jovyan/notebooks

RUN conda install --yes requests requests-oauthlib plotly nodejs qtpy pyqt pyqtgraph pyerfa astropy; \
    conda install -c conda-forge --yes ipywe lmfit; \
    conda clean --all --yes

RUN pip install PyQt5 neutronbraggedge NeuNorm sectorizedradialprofile inflect ImagingReso $PYONCAT_LOCATION

RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager; \
    jupyter nbextension enable --py widgetsnbextension; \    
    jupyter lab build
