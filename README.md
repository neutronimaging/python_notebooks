# Python Notebooks
This reporsitory provides various notebooks for users of the neutron imaging beamlines at ORNL. 
Full tutorial of most of the notebooks can be found at [here](https://neutronimaging.pages.ornl.gov/tutorial/).


## Instructions

The majority of the notebooks are ready to use on the ORNL cluster ([analysis cluster](https://analysis.sns.gov)) when logged in with your __XCAME__ account.
For those who wish to run these notebooks locally for
* light-weight data processing
* training and education
* development

__two methods__ are provided here to setup your personal environment to run these notebooks.

### Build Local Conda Environment

For most developers who wish to build on top of existing notebooks, it is recommended to build you own local environment such that additional dependencies and modules can be added to the `conda` env easily.
Here are the steps needed to build your own Conda env

* Install [`Anaconda3`](https://www.anaconda.com/products/individual) or [`miniconda3`](https://docs.conda.io/en/latest/miniconda.html).
  > If one of the two is already installed, skip this step.
* Create a virtual environment for this repo, e.g.
  ```bash
  conda create -n neutron_imaging python=3
  ```
* Activate the virtual environment with
  ```bash
  conda activate neutron_imaging
  ```
* You now need to bring the python notebooks repository to your computer
  
  **TODO**: we should specify here how to bring a tag version into their computer (zip, ...), then move to the repository
  
* Then use the provided bash script, `config_conda_env.sh`, to install required packages.
  ```bash
  bash config_conda_env.sh
  ```
  > NOTE: technically you can run this script in any environment, but it is __highly recommended__ to run it in a virual environment.

* Fire up your terminal, go to the root of this repo, and start the Jupyter notebook server with
  ```bash
  jupyter notebook
  ```
  You will see something similar to the following
  ```bash
    [I 14:00:13.183 NotebookApp] The port 8888 is already in use, trying another port.
    [I 14:00:14.061 NotebookApp] JupyterLab extension loaded from A_REALL_LONG_PATH
    [I 14:00:14.061 NotebookApp] JupyterLab application directory is ANOTHER_LONG_PATH
    [I 14:00:14.063 NotebookApp] Serving notebooks from local directory: CURRNT_DIR
    [I 14:00:14.063 NotebookApp] Jupyter Notebook 6.1.1 is running at:
    [I 14:00:14.063 NotebookApp] http://localhost:8889/?token=1e612467cf5e1e4f91cf074f483010ea7c8de989745eba96
    [I 14:00:14.063 NotebookApp]  or http://127.0.0.1:8889/?token=1e612467cf5e1e4f91cf074f483010ea7c8de989745eba96
    [I 14:00:14.063 NotebookApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
    [C 14:00:14.068 NotebookApp] 

    To access the notebook, open this file in a browser:
        file:///home/user/.local/share/jupyter/runtime/nbserver-2560206-open.html
    Or copy and paste one of these URLs:
        http://localhost:8889/?token=1e612467cf5e1e4f91cf074f483010ea7c8de989745eba96
        or http://127.0.0.1:8889/?token=1e612467cf5e1e4f91cf074f483010ea7c8de989745eba96

  ```
  Copy and paste the 6th line of the output to your browser
  ```bash
  http://localhost:8889/?token=1e612467cf5e1e4f91cf074f483010ea7c8de989745eba96
  ```
  and you are ready to use the notebooks.
  > NOTE: For most terminals, you can also `Ctrl+click` or `CMD+click` on the link to open it in your default browser. 

### Use pre-configured Docker image

A pre-configured docker image is available for those who do not wish to setup a local conda environment.
To use this approach, you need to install the [Docker desktop](https://www.docker.com/products/docker-desktop) on your local mahcine, which provides a Docker engine that manages all your containers.
> NOTE: Installation of `Docker Desktop` requires privileged access to the local system (as in using `sudo` on most Linux distro).  If you cannot perform this task due to security restrictions, please contact your IT support on how to enable docker for your account. 

Fire up your favorite terminal, and you can check if `docker` is properly installed on your system by
```bash
$ docker ps
```
which should show something similar to this
```bash
CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS              PORTS               NAMES
```

Then go to the root of this repository (if you haven't done so already), and use the following command to start the containerized notebook env
```bash
$ docker run --rm -p 9999:8888 -e JUPYTER_ENABLE_LAB=yes -v "$PWD":/home/jovyan/work kedokudo/neutron-imaging:latest
```
* `--rm`: remove the runtime container once your exit the notebook by pressing `Ctrl+C` in the terminal.  
  * If you would like to preserve the changes in the runtime container (for example, you might install some additional pacakges in the env). Replace `--rm` with `--name CONTAINER_NAME` where `CONTAINER_NAME` is the identifier you can use later to restart the container by 
  ```bash
  $ docker start CONTAINER_NAME
  ```
* `-p 9999:8888`: mapping the container internal port, `8888`, to the host port `9999` such that you can access Jupyter by going to `http://localhost:9999` on the host machine.
  * First time launching the Jupyter will ask you for a one time token, which you can find in the terminal output.  The easiest way to do this would be copy&past the link in the termial, and replace teh port number `8888` with `9999`.
* `-e JUPYTER_ENABLE_LAB=yes`: this allows you to use Jupyter lab instead of Jupyter notebook, which is very similar to Jupyter notebook, but with some additional features.
* `-v "$PWD":/home/jovyan/work`: mapping/mounting the current local directory (the root of repo) to `/home/jovyan/work` inside the container.
* `kedokudo/neutron-imaging:latest`: the image name and tag

> __WARNING__   
> On some system the port mapping is restricted by IT through a system wide policy or network-wide policy, which would prevent you from accessing the Jupyter inside the container.
> For such situation, you can either contact the IT to figure out a correct setting for your system, or try to run the container on a non-restricted machine/network. 

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
