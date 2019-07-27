#!/bin/bash -xe
WANT_ENV="docker-build docker-run"
. $(dirname $0)/env.sh

###########################
# Update system & install general dependencies
###########################

apt-get update
#${SUDO} apt-get upgrade -y

apt-get install -y \
    mesa-utils \
    libxi6 \
    libxkbcommon-x11-0 \
    libxslt1.1 \
    libxtst6 \
    libgl1-mesa-dri

# set Conda library search path
echo /opt/conda/lib | tee /etc/ld.so.conf.d/conda.conf
ldconfig

###########################
# Clean up
###########################
apt-get clean
