#!/bin/bash

export os=$(uname -s)
#export user=$(whoami)
#export uid=$(id -u)
#export gid=$(id -g)

case ${os} in
    Linux*)     X11=${DISPLAY};;
    Darwin*)    X11=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}'):0;;
    CYGWIN*)    X11=${DISPLAY};;
    MINGW*)     X11=${DISPLAY};;
    *)          echo "UNSUPPORTED OS: ${os}"; exit 1
esac

xhost +
docker build -t neutron-imaging .
docker run -v ${HOME}:/home/jovyan/work -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=${X11} -p 8888:8888 neutron-imaging
