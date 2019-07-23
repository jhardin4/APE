# -*- coding: utf-8 -*-
import logging
from inspect import isclass

from qtpy.QtCore import QObject, Signal, Property, Slot

import Devices
from Devices import Motion

from ..apparatus import AppInterface

logger = logging.getLogger('MotionDevices')


class MotionDevices(QObject):
    appInterfaceChanged = Signal()

    devicesChanged = Signal()

    def __init__(self, parent=None):
        super(MotionDevices, self).__init__(parent)

        self._app_interface = None
        self._devices = []

    @Property(AppInterface, notify=appInterfaceChanged)
    def appInterface(self):
        return self._app_interface

    @appInterface.setter
    def appInterface(self, new_interface):
        if new_interface == self._app_interface:
            return
        old_interface = self._app_interface
        self._app_interface = new_interface
        self.appInterfaceChanged.emit()

        if old_interface:
            old_interface.appImageChanged.disconnect(self.refresh)
        if new_interface:
            new_interface.appImageChanged.connect(self.refresh)
            self.refresh()

    @Slot()
    def refresh(self):
        if not self._app_interface:
            logger.debug("Cannot refresh without an appInterface")
            return

        motion_devices = []
        data = self._app_interface.app_image
        for name, device in data.get('devices', dict()).items():
            type_ = device['type'].value
            class_ = getattr(Devices, type_, None)
            if isclass(class_) and issubclass(class_, Motion):
                motion_devices.append(name)

        self._devices = motion_devices
        self.devicesChanged.emit()

    @Property(list, notify=devicesChanged)
    def devices(self):
        return self._devices
