#!/bin/bash -xe
WANT_ENV="docker-build docker-run"
. $(dirname $0)/env.sh

# Ensure apt cache is up to date
apt-get update

###########################
# Tools
###########################

pip install \
    black \
    pre-commit \
    flake8 \
    pep8-naming \
    python-qt-live-coding \
    pytest-qt

apt-get install -y \
    cmake \
    g++ \
    mesa-common-dev

# Install QML QA tools
# don't need to install any dependencies since Qt is installed with ROS
QMLFMT_BUILD_DIR=${QMLFMT_BUILD_DIR:-${WS_DIR}/qmlfmt}
git clone https://github.com/machinekoder/qmlfmt.git "${QMLFMT_BUILD_DIR}"
cd "${QMLFMT_BUILD_DIR}"
cmake .
make -j$(nproc)
make install

###########################
# Clean up
###########################
apt-get clean
rm -rf ${QMLFMT_BUILD_DIR}
if test_environment docker-build; then
    rm -rf /root/.ccache
fi
