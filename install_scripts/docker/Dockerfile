ARG DEBIAN_SUITE
FROM continuumio/anaconda3:latest

# ARG HTTP_PROXY

# Configure & update apt
# - Silence some Apt warnings
ENV DEBIAN_FRONTEND noninteractive
RUN echo 'APT::Install-Recommends "0";\nAPT::Install-Suggests "0";' > \
        /etc/apt/apt.conf.d/01norecommend

# - Update local Debian mirrors
# ARG DEBIAN_SUITE
# ARG DEBIAN_MIRROR=deb.debian.org
# ARG DEBIAN_SECURITY_MIRROR=security.debian.org
# RUN bash -c "( \
#         echo deb http://${DEBIAN_MIRROR}/debian ${DEBIAN_SUITE} main; \
#         echo deb http://${DEBIAN_MIRROR}/debian ${DEBIAN_SUITE}-updates main; \
#         echo deb http://${DEBIAN_SECURITY_MIRROR}/debian-security \
#             ${DEBIAN_SUITE}/updates main; \
#         ) | tee /etc/apt/sources.list"
# # - Set HTTP proxy for Apt
# RUN test -z "${HTTP_PROXY}" || \
#     echo "Acquire::http::Proxy \"${HTTP_PROXY}\";" \
#     | tee /etc/apt/apt.conf.d/42proxy

# # - Upgrade packages
RUN apt-get update
RUN apt-get upgrade -y && \
    apt-get clean
# - Silence more Apt warnings
RUN apt-get install -y \
#    software-properties-common \
    libfile-fcntllock-perl \
    && apt-get clean

# Install and configure sudo, passwordless for everyone
RUN apt-get install -y \
    sudo && \
    apt-get clean
RUN echo "ALL	ALL=(ALL:ALL) NOPASSWD: ALL" >> /etc/sudoers

# Cookie variable for container build environment
ENV ENV_COOKIE docker-build

# HTTP proxy for wget, etc.
ENV http_proxy ${HTTP_PROXY}

###########################################
# Install packages
#
# Customize the following for building/running targeted software

# Install misc. packages
ARG EXTRA_PACKAGES
RUN apt-get install -y \
    ccache \
    gnupg2 \
    ${EXTRA_PACKAGES} \
    && apt-get clean

# Copy install scripts; only copy modular parts on demand so they can
# be fixed without dirtying the Docker cache
COPY env.sh /tmp/install/

# Update system & install general dependencies
COPY 1-system.sh /tmp/install/
RUN /tmp/install/1-system.sh

# Build and install nvidia graphics driver
COPY 2-glx.sh /tmp/install/
RUN /tmp/install/2-glx.sh

# Build and install devel stuff
COPY 3-tools.sh /tmp/install/
RUN /tmp/install/3-tools.sh

# Final cleanup
RUN rm -rf /tmp/install

# Image version for adding to the environment
ARG IMAGE_VERSION

ENV \
    # Speed builds with ccache
    PATH=/usr/lib/ccache:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin \
    # Set image version for internal sanity checks
    IMAGE_VERSION=${IMAGE_VERSION} \
    # disable Pythons .local import path
    PYTHONNOUSERSITE=True

# Cookie variable for container run environment
ENV ENV_COOKIE docker-run

###########################################
# Set up user
#

# This shell script adds passwd and group entries for the user
COPY entrypoint.sh /usr/bin/entrypoint
ENTRYPOINT ["/usr/bin/entrypoint"]
# If no args to `docker run`, start an interactive shell
CMD ["/bin/bash", "--login", "-i"]
