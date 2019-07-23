#!/bin/bash -xe
WANT_ENV="docker-build docker-run"
. $(dirname $0)/env.sh

# Ensure apt cache is up to date
apt-get update

###########################
# Tools
###########################

pip install \
    opencv-python \
    pyueye

pip uninstall --yes \
    enum34

###########################
# Clean up
###########################
apt-get clean
if test_environment docker-build; then
    rm -rf /root/.ccache
fi
