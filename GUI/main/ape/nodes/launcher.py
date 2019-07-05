# -*- coding: utf-8 -*-
import logging

from qtpy.QtCore import QObject, Signal, Property, Slot

from MultiProcess.zmqNode import zmqNode

logger = logging.getLogger("Launcher")


class Launcher(QObject):
    l2aAddressChanged = Signal(str)
    l2peAddressChanged = Signal(str)
    l2gAddressChanged = Signal(str)
    a2peAddressChanged = Signal(str)
    a2gAddressChanged = Signal(str)
    g2peAddressChanged = Signal(str)

    def __init__(self, parent=None):
        super(Launcher, self).__init__(parent)

        self._node = zmqNode('launcher')
        self._node.logging = True
        self._node.start_listening()

        port = 5575
        self._l2a_address = "tcp://127.0.0.1:" + str(port)
        self._l2pe_address = "tcp://127.0.0.1:" + str(port + 1)
        self._l2g_address = "tcp://127.0.0.1:" + str(port + 2)
        self._a2pe_address = "tcp://127.0.0.1:" + str(port + 3)
        self._a2g_address = "tcp://127.0.0.1:" + str(port + 4)
        self._g2pe_address = "tcp://127.0.0.1:" + str(port + 5)
        self._connect()

    @Slot()
    def start(self):
        self._connect()

    @Slot()
    def stop(self):
        self._node.close()

    def _connect(self):
        self._node.connect('appa', self._l2a_address, server=True)
        self._node.connect('procexec', self._l2pe_address, server=True)
        self._node.connect('gui', self._l2g_address, server=True)

    def send_close_all(self):
        for connection in self._node.connections:
            self.send_close(connection)
        logger.debug('Close commands sent')

    def send_close(self, connection):
        message = {'subject': 'close'}
        self._node.send(connection, message)

    @Property(str, notify=l2aAddressChanged)
    def l2aAddress(self):
        return self._l2a_address

    @Property(str, notify=l2peAddressChanged)
    def l2peAddress(self):
        return self._l2pe_address

    @Property(str, notify=l2gAddressChanged)
    def l2gAddress(self):
        return self._l2g_address

    @Property(str, notify=a2peAddressChanged)
    def a2peAddress(self):
        return self._a2pe_address

    @Property(str, notify=a2gAddressChanged)
    def a2gAddress(self):
        return self._a2g_address

    @Property(str, notify=g2peAddressChanged)
    def g2peAddress(self):
        return self._g2pe_address
