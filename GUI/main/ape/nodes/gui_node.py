import logging

from qtpy.QtCore import QObject, Slot, Signal, Property

from MultiProcess.APE_Interfaces import ApparatusInterface, ExecutorInterface
from MultiProcess.zmqNode import zmqNode

from .launcher import Launcher

logger = logging.getLogger('GuiNode')


class GuiNode(QObject):
    launcherChanged = Signal(Launcher)
    runningChanged = Signal(bool)

    def __init__(self, parent=None):
        super(GuiNode, self).__init__(parent)

        self._running = False
        self._launcher = None
        self._node = None
        self._apparatus = None
        self._executor = None

    @Slot()
    def start(self):
        if self._running:
            logger.debug('already running')
            return
        if not self._launcher:
            logger.error('need a launcher to start')
            return

        # Create the node
        self._node = zmqNode('gui')
        self._node.logging = True
        # self.User = Devices.User_GUI('User')
        # Create an interface for the executor and apparatus
        # assigns them to the gui
        self._apparatus = ApparatusInterface(self._node)
        self._executor = ExecutorInterface(self._node)
        # connect to launcher, apparatus, and procexec
        self._node.connect('appa', self._launcher.a2gAddress)
        self._node.connect('procexec', self._launcher.g2peAddress)
        self._node.connect('launcher', self._launcher.l2gAddress)
        # sets the target to be the GUI
        self._node.target = self
        # sets the interface apparatus to the apparatus in the GUI

        self._node.start_listening()

        self._running = True
        self.runningChanged.emit(True)

    @Slot()
    def stop(self):
        if not self._running:
            logger.debug('already stopped')
            return
        if not self._launcher:
            logger.error('need a launcher to stop')
            return

        self._launcher.send_close('gui')
        self._node.close()
        self._node = None
        self._apparatus = None
        self._executor = None

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

    @property
    def apparatus(self):
        return self._apparatus

    @property
    def executor(self):
        return self._executor
