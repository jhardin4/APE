# APE_GUI

## QA Dependencies

Install the QA dependencies:

```bash
pip install pre-commit black flake8 pytest-qt
```

## Coding style

### Pre-Commit
The Docker container comes with [pre-commit](https://pre-commit.com/) installed.
pre-commit is a pre-commit framework which can be attached as git hook. It
runs code-formatting and other checks automatically before committing any code.
You just need to install with:

```bash
pre-commit install
pre-commit autoupdate
```

### Python

For Python we can use [black](https://github.com/ambv/black):

```bash
black -S .
```

**NOTE:** The `-S` parameter prevents black from changing quotes.

## Docker dev environment and CI

The `install_scripts` directory contains a Docker configuration as well as helper
scripts to set up a Docker-based development and CI environment.

The Docker setup is meant to be built on Linux or with the Windows Subsystem for Linux.
The Windows Subsystem for Linux setup has following requirements:

* Docker Host installed on Windows: <https://docs.docker.com/docker-for-windows/>
* Windows Subsystem for Linux installation of Ubuntu 18.04: <https://docs.microsoft.com/en-us/windows/wsl/install-win10>
* Docker client installed in Ubuntu: <https://medium.com/@sebagomez/installing-the-docker-client-on-ubuntus-windows-subsystem-for-linux-612b392a44c4>
* Windows file paths mounted to `/c` and not `/mnt/c`: <https://nickjanetakis.com/blog/setting-up-docker-for-windows-and-wsl-to-work-flawlessly>
* APE repo cloned to subdirectory of the `C:\Users\<name>` directory (e.g. `C:\Users\Alexander\repos\APE`)

The image can be built and run using the `docker-dev.sh` script.

### Image build

Build a new development/CI image.

```bash
./install_scripts/docker-dev.sh -b
```

### Development environment

Automatically pulls a new image if necessary.

```bash
./install_scripts/docker-dev.sh
```

### Push image to Docker Hub

Pushes the image to Docker-Hub.

```bash
./install_scripts/docker-dev.sh -p
```

### Bump image version

The script generates a hash which identifies the Docker image. This features is used to synchronise Docker images
with git repo versions. To generate a new hash (if necessary) run following command:

```bash
./install_scripts/docker-dev.sh -B
```


## Live Coding

Live-coding speeds up development of Qt/QML applications.

Before using live-coding you need to install the [python-qt-live-coding](https://github.com/machinekoder/python-qt-live-coding) package from PyPi.

```bash
pip install python-qt-live-coding
```

The GUI can be started in live-coding mode using following commands:
```bash
python gui.py --live
```
