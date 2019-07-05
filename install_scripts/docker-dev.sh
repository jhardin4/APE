#!/bin/bash -e

usage() {
    if test -z "$*"; then
        RC=0
    else
        echo "Error:  $*" >&2
        RC=1
    fi
    cat >&2 <<EOF
Usage: $0 [args]
      run args:  [-n NAME] [-t IMAGE] [-N] [-l LINK] [CMD [ARG ...]]
    build args:  -b [-t IMAGE] [-N] [-- docker build args]
 bump-ver args:  -B
     push args:  -p [-N]
 check-env args: -c

EOF
    exit $RC
}

while getopts :bBpct:N-n:l:h ARG; do
    case $ARG in
    # Script mode (default:  docker run)
    b) BUILD=true ;;
    B)
        BUMP_IMAGE_VERSION=true
        WANT_ENV='bare-metal docker-run'
        ;;
    p) PUSH=true ;;
    # Global options
    t)
        IMAGE_BASE=$OPTARG
        USE_OVERLAY=false
        ;;
    N) USE_OVERLAY=false ;;
    -) break ;; # Following args passed to docker command
    # Run options
    n) NAME=$OPTARG ;;
    l) LINK_CONTAINER=$OPTARG ;;
    c) CHECK_ENV=true ;;
    # Usage
    h) usage ;;
    :) usage "Option -$OPTARG requires an argument" ;;
    *) usage "Illegal option -$OPTARG" ;;
    esac
done
shift $(($OPTIND - 1))

# Set params
# - Build image? (-b)
BUILD=${BUILD:-false}
# - Bump image version? (-B)
BUMP_IMAGE_VERSION=${BUMP_IMAGE_VERSION:-false}
# - Push image? (-p)
PUSH=${PUSH:-false}
# - Container name (-n)
NAME=${NAME:-ape}
# - Container name to link (-l NAME):  for sim
LINK_CONTAINER=${LINK_CONTAINER:+--link=${LINK_CONTAINER}}
# - Check if running bare metal? (-c)
CHECK_ENV=${CHECK_ENV:-false}

# Read common settings
WANT_ENV="${WANT_ENV:-bare-metal}"
if ${CHECK_ENV}; then
    WANT_ENV_CHECK="${WANT_ENV}"
    WANT_ENV=
fi
source "$(dirname $0)/docker/env.sh"

###########################
# Check wanted environment
if ${CHECK_ENV}; then
    if test_environment ${WANT_ENV_CHECK}; then
        exit 0 # outside docker
    else
        exit 1 # in docker
    fi
fi

###########################
# Bump image version
if ${BUMP_IMAGE_VERSION}; then
    echo "Bumping image version"
    save_image_version
    $BUILD || exit $(test -z ${IMAGE_VERSION_UPDATED})
fi

###########################
# Docker build base or overlay image
if $BUILD; then
    if ! ${USE_OVERLAY}; then
        # Build base image when -N is supplied
        # - Use a local mirror if specified
        test -z "${DEBIAN_MIRROR}" || DOCKER_DEV_BUILD_OPTS+=(
            --build-arg DEBIAN_MIRROR=${DEBIAN_MIRROR})
        test -z "${DEBIAN_SECURITY_MIRROR}" || DOCKER_DEV_BUILD_OPTS+=(
            --build-arg DEBIAN_SECURITY_MIRROR=${DEBIAN_SECURITY_MIRROR})
        test -z "${HTTP_PROXY}" || DOCKER_DEV_BUILD_OPTS+=(
            --build-arg HTTP_PROXY=${HTTP_PROXY})
        # - Docker build
        set -x
        exec docker build -t "${IMAGE_BASE}" \
            --build-arg ROS_DISTRO=$ROS_DISTRO \
            --build-arg DEBIAN_SUITE=$DEBIAN_SUITE \
            --build-arg IMAGE_VERSION=$IMAGE_VERSION \
            "${DOCKER_DEV_BUILD_OPTS[@]}" \
            ${BUILD_ARGS} \
            "$@" "${DOCKER_SCRIPTS_DIR}"
    else
        # Build the overlay image when -N isn't supplied
        # - OVERLAY_DIR may be set in the rc file or the environment
        test -z "${OVERLAY_DIR}" && usage "Please specify overlay directory"
        test -d "${OVERLAY_DIR}" ||
            usage "Overlay directory ${OVERLAY_DIR} does not exist"
        # - Docker build
        set -x
        exec docker build -t "${IMAGE_OVERLAY}" \
            --build-arg IMAGE_BASE="${IMAGE_BASE}" \
            ${OVERLAY_DOCKER_PATH:+--file=${OVERLAY_DOCKER_PATH}} \
            "${DOCKER_DEV_OVERLAY_BUILD_OPTS[@]}" \
            ${OVERLAY_BUILD_ARGS} \
            "$@" \
            "${OVERLAY_DIR}"
    fi
fi

###########################
# Docker push
if $PUSH; then

    set -x
    exec docker push ${IMAGE}
fi

###########################
# Docker run

# Check for existing containers
EXISTING="$(docker ps -aq --filter=name=^/${NAME}$)"
RUNNING=false
if test -n "${EXISTING}"; then
    # Container exists; is it running?
    RUNNING=$(docker inspect ${NAME} | awk -F '[ ,]+' '/"Running":/ { print $3 }')
    if test "${RUNNING}" = "false"; then
        # FIXME If container exists but stopped, what to do?
        echo "Error:  Container '${NAME}' exists but stopped" >&2
        echo "Please fix this and restart this script" >&2
        exit 1
    elif test "${RUNNING}" = "true"; then
        echo "Container '${NAME}' already running" >&2
    else
        # Something went wrong
        echo "Error:  unable to determine status of " \
            "existing container '${EXISTING}'" >&2
        exit 1
    fi
else
    # Container doesn't exist yet; detect hardware

    # - Video driver
    case "${OGL_VENDOR}::${OGL_RENDERER}" in
    "Intel Open Source Technology Center"::*) # Brix; John's ThinkPad X201t
        echo "Detected Intel graphics card"
        # No special config
        ;;
    "NVIDIA Corporation"::*) # Alexander's NVidia w/proprietary drivers
        echo "Detected NVIDIA graphics card"
        DOCKER_DEV_OPTS+=(
            --privileged
            --runtime=nvidia
            -e NVIDIA_VISIBLE_DEVICES=all
            -e NVIDIA_DRIVER_CAPABILITIES=graphics
        )
        ;;
    "VMware, Inc."::*) # SSH forwarded X connection
        # (Probably will never see this)
        echo "Detected virtual graphics hardware"
        echo "WARNING:  The robot_ui will not run with this hardware!"
        ;;
    "nouveau"::*) # Bas's NVidia w/FOSS drivers
        echo "Detected Nouveau driver"
        # No special config
        ;;
    "X.Org"::*POLARIS*) # Rob's AMD RX 580 GPU
        echo "Detected Polaris driver"
        DOCKER_DEV_OPTS+=(-v /dev/kfd:/dev/kfd)
        ;;
    *)
        echo "Unable to detect graphics hardware"
        echo "WARNING:  The robot_ui may not run with this hardware!"
        echo "Please add your hardware to the '$0' script"
        ;;
    esac
fi

if tty -s; then
    # interactive shell
    DOCKER_INTERACTIVE=-i
fi

# Give the user a shell
if ! ${RUNNING}; then
    # No existing container; start new one
    C_UID=$(id -u)
    C_GID=$(id -g)

    set -x
    exec docker run --rm \
        ${DOCKER_INTERACTIVE} \
        -t \
        --network host \
        -e UID=${C_UID} \
        -e GID=${C_GID} \
        -e QT_X11_NO_MITSHM=1 \
        -e XDG_RUNTIME_DIR \
        -e HOME \
        -e USER \
        -e TERM \
        -e DISPLAY \
        -e debian_chroot="${NAME}@${IMAGE_VERSION}" \
        -v /tmp/.X11-unix:/tmp/.X11-unix \
        -v /dev/dri:/dev/dri \
        -v $HOME:$HOME \
        -v $PWD:$PWD \
        -v $XDG_RUNTIME_DIR:$XDG_RUNTIME_DIR \
        -e DBUS_SESSION_BUS_ADDRESS \
        -v /var/run/dbus/system_bus_socket:/var/run/dbus/system_bus_socket \
        -w $PWD \
        -h ${NAME} --name ${NAME} \
        "${DOCKER_DEV_OPTS[@]}" \
        ${LINK_CONTAINER} \
        ${IMAGE} "$@"
        # add --privileged for hardware device access
else
    # Container already started:  Exec a new shell in the existing container
    if test -z "$*"; then
        set -x
        exec docker exec ${DOCKER_INTERACTIVE} -tu ${USER} ${NAME} bash -i
    else
        set -x
        exec docker exec ${DOCKER_INTERACTIVE} -tu ${USER} ${NAME} "$@"
    fi
fi
