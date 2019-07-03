#!/bin/bash -e
#######################################
# Initialize and build ROS workspace
#######################################

# Set up environment
WANT_ENV=docker-run
source "$(dirname $0)/../install_scripts/docker/env.sh"
cd "${REPO_DIR}"

# install pre-commit hook
pre-commit install -f
mv .git/hooks/pre-commit .git/hooks/pre-commit-run
cp -v install_scripts/include/pre-commit .git/hooks/pre-commit
