import logging

from qtpy.QtCore import QObject, Slot, Signal, Property

from MultiProcess.APE_Interfaces import ApparatusInterface, ExecutorInterface
from MultiProcess.zmqNode import zmqNode

logger = logging.getLogger('GuiNode')


class GuiNode(QObject):
    runningChanged = Signal(bool)
    a2gAddressChanged = Signal(str)
    g2peAddressChanged = Signal(str)
    l2gAddressChanged = Signal(str)

    def __init__(self, parent=None):
        super(GuiNode, self).__init__(parent)

        self._running = False
        self._node = None
        self._apparatus = None
        self._executor = None

        self._a2g_address = ''
        self._g2pe_address = ''
        self._l2g_address = ''

    @Property(str, notify=a2gAddressChanged)
    def a2gAddress(self):
        return self._a2g_address

    @a2gAddress.setter
    def a2gAddress(self, value):
        if value == self._a2g_address:
            return
        self._a2g_address = value
        self.a2gAddressChanged.emit(value)

    @Property(str, notify=g2peAddressChanged)
    def g2peAddress(self):
        return self._g2pe_address

    @g2peAddress.setter
    def g2peAddress(self, value):
        if value == self._g2pe_address:
            return
        self._g2pe_address = value
        self.g2peAddressChanged.emit(value)

    @Property(str, notify=l2gAddressChanged)
    def l2gAddress(self):
        return self._l2g_address

    @l2gAddress.setter
    def l2gAddress(self, value):
        if value == self._l2g_address:
            return
        self._l2g_address = value
        self.l2gAddressChanged.emit(value)

    @Slot()
    def start(self):
        if self._running:
            logger.debug('already running')
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
        self._node.connect('appa', self._a2g_address)
        self._node.connect('procexec', self._g2pe_address)
        self._node.connect('launcher', self._l2g_address)
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

        self._node.close()
        self._node = None
        self._apparatus = None
        self._executor = None

        self._running = False
        self.runningChanged.emit(False)

    @Property(bool, notify=runningChanged)
    def running(self):
        return self._running

    @property
    def apparatus(self):
        return self._apparatus

    @property
    def executor(self):
        return self._executor
