import multiprocessing
import logging

from GUI.launcher import LauncherGui

if __name__ == '__main__':
    # enable application debug logging
    logging.basicConfig(level=logging.DEBUG)
    # this is important to avoid forking in UNIX operating systems
    multiprocessing.set_start_method('spawn')
    # launch the launcher GUI
    LauncherGui.start()
