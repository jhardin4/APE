# Set up environment parameters used by both Docker and bare-metal
# scripts

# Allow variables to be customized here
if test -e ~/.ape_docker.conf; then
    source ~/.ape_docker.conf
fi

# Debugging
test "$DEBUG" = true || DEBUG=false

# Directory paths
# - The install_scripts/docker directory
DOCKER_SCRIPTS_DIR="$(readlink -f $(dirname "${BASH_SOURCE[0]}"))"
# - The install_scripts directory (keep this relative to DOCKER_SCRIPTS_DIR)
INSTALL_SCRIPTS_DIR="$(readlink -f "${DOCKER_SCRIPTS_DIR}"/..)"
# - The base repo directory
REPO_DIR="$(readlink -f "${DOCKER_SCRIPTS_DIR}"/../..)"
# - The install_scripts/bare_metal directory
BARE_METAL_SCRIPTS_DIR="${INSTALL_SCRIPTS_DIR}/bare_metal"
# - The devel_scripts directory
DEVEL_SCRIPTS_DIR="${REPO_DIR}/devel_scripts)"
# - Where to cache install artifacts
CACHE_DIR="${CACHE_DIR:-/tmp/install-cache-$(id -un)}"

# Guarantee the script is running in one of these environments, or bail
ENV_COOKIE=${ENV_COOKIE:-bare-metal} # docker-build, docker-run, bare-metal
test_environment() {
    # test_environment [ bare-metal | docker-build | docker-run ]
    # return true if current environment matches one on the cmdline, else false
    local e
    for e in $*; do
        if test ${ENV_COOKIE:-bare-metal} = $e; then
            return 0
        fi
    done
    return 1
}
assert_environment() {
    if test_environment $*; then
        return # We're running in the right place
    fi
    echo "This script is not meant for running in the" \
        "${ENV_COOKIE} environment" >&2
    exit 1
}
# - Run assert_environment now if instructed
test -z "${WANT_ENV}" || assert_environment ${WANT_ENV}

# Set & create build directory
WS_DIR=${WS_DIR:-~/ws_dir}

###########################
# Detect CPU configuration
###########################

# Clean up after scripts?
if test_environment docker-build; then
    CLEANUP=true
else
    CLEANUP=${CLEANUP:-false}
fi

# Executables
# - sudo
if $DEBUG; then
    SUDO=echo
    DO=echo
    APT_GET="sudo DEBIAN_FRONTEND=noninteractive apt-get"
elif test $(id -u) != 0; then
    # If this is defined but blank, sudo will not be used
    SUDO="${SUDO-sudo}"
    DO=
    APT_GET="${SUDO-env} DEBIAN_FRONTEND=noninteractive apt-get"
else
    SUDO=
    DO=
    APT_GET="env DEBIAN_FRONTEND=noninteractive apt-get"
fi

# Variables to customize in preseed.cfg
DEBIAN_MIRROR=${DEBIAN_MIRROR:-http.us.debian.org}
DEBIAN_SECURITY_MIRROR=${DEBIAN_SECURITY_MIRROR:-security.debian.org}
DEBIAN_CD_MIRROR=${DEBIAN_CD_MIRROR:-cdimage.debian.org}
POST_INSTALL_CMD=${POST_INSTALL_CMD:-:}

# GPU variables
if which glxinfo >&/dev/null; then
    glx_string() { glxinfo -display :0 | sed -n "/${1}/ s/^.*: // p"; }
    OGL_VENDOR="$(glx_string "OpenGL vendor string")"
    OGL_RENDERER="$(glx_string "OpenGL renderer string")"
fi

# Current OS info
OS_VENDOR=$(
    . /etc/os-release
    echo $ID
) # debian, ubuntu
OS_VERSION=$(
    . /etc/os-release
    echo $VERSION_ID
) # 16.04

# Set http proxy for wget
test -z "${HTTP_PROXY}" || export http_proxy=${HTTP_PROXY}

# Docker image version
compute_image_minor_version() {
    # Use first 8 chars of a sha1sum of files in the docker/ directory
    (
        cd $DOCKER_SCRIPTS_DIR
        find . -type f -print0 |
            sort -z |
            xargs -0 sha1sum |
            sha1sum |
            sed 's/^\(........\).*/\1/'
    )
}
update_image_vars() {
    # Image version
    IMAGE_VERSION=${IMAGE_VERSION:-$IMAGE_VERSION_MAJOR.$IMAGE_VERSION_MINOR}
    IMAGE_TAG=$TAG-$IMAGE_VERSION
    # Base image name
    IMAGE_BASE=${IMAGE_BASE:-$IMAGE_BASE_ID/$IMAGE_REPO:$IMAGE_TAG}
    # Overlay image name
    IMAGE_OVERLAY=${OVERLAY_REPO}:$IMAGE_TAG

    # Final image to use
    if ${USE_OVERLAY}; then
        IMAGE=${IMAGE_OVERLAY}
    else
        IMAGE=${IMAGE_BASE}
    fi
}
bump_image_version() {
    NEW_IMAGE_VERSION_MINOR=$(compute_image_minor_version)
    if test "${FILE_IMAGE_VERSION_MINOR}" = "${NEW_IMAGE_VERSION_MINOR}"; then
        echo "Image minor version=${FILE_IMAGE_VERSION_MINOR} unchanged" >&2
        return
    fi
    OLD_IMAGE_VERSION_MAJOR=${IMAGE_VERSION_MAJOR:-0}
    IMAGE_VERSION_MAJOR=$(($OLD_IMAGE_VERSION_MAJOR + 1))
    OLD_IMAGE_VERSION_MINOR=${IMAGE_VERSION_MINOR:-00000000}
    IMAGE_VERSION_MINOR=$(compute_image_minor_version)
    update_image_vars
    IMAGE_VERSION_UPDATED="true"
}
save_image_version() {
    bump_image_version
    {
        echo "IMAGE_VERSION_MAJOR=$IMAGE_VERSION_MAJOR"
        echo "IMAGE_VERSION_MINOR=$IMAGE_VERSION_MINOR"
    } >"$IMAGE_VERSION_FILE"
    # Debugging
    echo "$IMAGE_VERSION_FILE:"
    cat "$IMAGE_VERSION_FILE"
}
# - Read from file
IMAGE_VERSION_FILE="$INSTALL_SCRIPTS_DIR/image-version.sh"
if test -f "$IMAGE_VERSION_FILE"; then
    source "$IMAGE_VERSION_FILE"
    FILE_IMAGE_VERSION_MINOR=${IMAGE_VERSION_MINOR}
    FILE_IMAGE_VERSION_MAJOR=${IMAGE_VERSION_MAJOR}
fi
# - Major version defaults to zero
IMAGE_VERSION_MAJOR=${IMAGE_VERSION_MAJOR:-0}
# - Minor version
IMAGE_VERSION_MINOR=${IMAGE_VERSION_MINOR:-00000000}
# - Check for changes
IMAGE_VERSION_CURRENT_MINOR="$(compute_image_minor_version)"
if test "${FILE_IMAGE_VERSION_MINOR}" != "${IMAGE_VERSION_CURRENT_MINOR}"; then
    echo "WARNING:  Image version changed: " \
        "${FILE_IMAGE_VERSION_MINOR} != ${IMAGE_VERSION_CURRENT_MINOR}" >&2
    echo "WARNING:  Consider bumping saved version and building a new image" >&2
fi

# Set up Docker image variables
# - image name components
IMAGE_BASE_ID=${IMAGE_BASE_ID:-machinekoder}
IMAGE_REPO=${IMAGE_REPO:-ape}
TAG=${TAG:-dev}
# - use overlay image if an overlay path or ID is set
test -z "${OVERLAY_PATH}" -a -z "${OVERLAY_REPO}" ||
    USE_OVERLAY=${USE_OVERLAY:-true}
USE_OVERLAY=${USE_OVERLAY:-false}
# - generate base and overlay image names
update_image_vars
if $DEBUG; then
    echo "IMAGE_VERSION=${IMAGE_VERSION}" >&2
    echo "IMAGE_BASE=${IMAGE_BASE}" >&2
    test -z "$USE_OVERLAY" || echo "IMAGE_OVERLAY=${IMAGE_OVERLAY}" >&2
fi
