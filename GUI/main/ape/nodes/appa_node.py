# -*- coding: utf-8 -*-
import logging

from qtpy.QtCore import QObject, Slot, Property, Signal
from MultiProcess.Appa import Appa
from multiprocessing import Process

from .launcher import Launcher

logger = logging.Logger('AppNode')


class AppaNode(QObject):
    launcherChanged = Signal(Launcher)
    runningChanged = Signal(bool)

    def __init__(self, parent=None):
        super(AppaNode, self).__init__(parent)

        self._process = None
        self._launcher = None
        self._running = False

    @Slot()
    def start(self):
        if self._process:
            logger.warning('already started')
            return
        if not self._launcher:
            logger.error('need a launcher to start')
        self._process = Process(
            target=Appa,
            args=(
                self._launcher.l2aAddress,
                self._launcher.a2peAddress,
                self._launcher.a2gAddress,
            ),
        )
        self._process.start()

        self._running = True
        self.runningChanged.emit(True)

    @Slot()
    def stop(self):
        if not self._process:
            logger.warning('already stopped')
            return
        self._launcher.send_close('appa')
        self._process.join()
        self._process = None
        self._running = False
        self.runningChanged.emit(False)

    @Property(Launcher, notify=launcherChanged)
    def launcher(self):
        return self._launcher

    @launcher.setter
    def launcher(self, value):
        if value == self._launcher:
            return
        self._launcher = value
        self.launcherChanged.emit(value)

    @Property(bool, notify=runningChanged)
    def running(self):
        return self._running
