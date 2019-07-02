#!/bin/bash -e

# add hostname to hosts
sh -c 'echo "127.0.2.1  `hostname`" >> /etc/hosts'

# Add user and group to system
echo "${USER}:x:${UID}:${GID}::${HOME}:/bin/bash" >>/etc/passwd
echo "${USER}:x:${GID}:" >>/etc/group
sed -i '/.*sudo.*:/ s/$/'${USER}'/' /etc/group

# Set up nvidia graphics

if [[ -z "${NVIDIA_VISIBLE_DEVICES}" ]]; then
    LIBGL=$(dpkg -L libgl1-mesa-glx | grep libGL.so\..\..\..)
    ln -sf ${LIBGL} /usr/lib/x86_64-linux-gnu/libGL.so
    ln -sf ${LIBGL} /usr/lib/x86_64-linux-gnu/libGL.so.1
fi

echo -e "conda activate base" >> /etc/profile.d/conda_activate.sh

# Run command as user
default_cmd=(/bin/bash --login -i)
exec sudo -u ${USER} -E "${@:-${default_cmd[@]}}"
