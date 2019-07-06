# -*- coding: utf-8 -*-
import logging

from qtpy.QtCore import QObject, Slot, Property, Signal

from MultiProcess.ProcExec import ProcExec
from MultiProcess.Appa import Appa
from multiprocessing import Process

from .launcher import Launcher
from .gui_node import GUI_Node

logger = logging.getLogger('AppNode')


class Node(QObject):
    launcherChanged = Signal(Launcher)
    runningChanged = Signal(bool)

    def __init__(self, parent=None):
        super(Node, self).__init__(parent)

        self._process = None
        self._launcher = None
        self._running = False

        self.destroyed.connect(lambda: self._shutdown())

    def _shutdown(self):
        if self._process:
            self.stop()

    def _start_process(self, target, args):
        if self._process:
            logger.debug('already started')
            return
        if not self._launcher:
            logger.error('need a launcher to start')
            return
        logger.debug('starting {}'.format(target.__name__))
        self._process = Process(target=target, args=args)
        self._process.start()

        self._running = True
        self.runningChanged.emit(True)

    def _stop_process(self, cmd):
        if not self._process:
            logger.debug('already stopped')
            return
        if not self._launcher:
            logger.error('need a launcher to stop')
            return
        logger.debug('stopping {}'.format(cmd))
        self._launcher.send_close(cmd)
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


class AppaNode(Node):
    @Slot()
    def start(self):
        self._start_process(
            target=Appa,
            args=(
                self._launcher.l2aAddress,
                self._launcher.a2peAddress,
                self._launcher.a2gAddress,
            ),
        )

    @Slot()
    def stop(self):
        self._stop_process('appa')


class ProcExecNode(Node):
    @Slot()
    def start(self):
        self._start_process(
            target=ProcExec,
            args=(
                self._launcher.l2peAddress,
                self._launcher.a2peAddress,
                self._launcher.g2peAddress,
            ),
        )

    @Slot()
    def stop(self):
        self._stop_process('procexec')


class GuiNode(Node):
    @Slot()
    def start(self):
        self._start_process(
            target=GUI_Node,
            args=(
                self._launcher.l2gAddress,
                self._launcher.a2gAddress,
                self._launcher.g2peAddress,
            ),
        )

    @Slot()
    def stop(self):
        self._stop_process('gui')
