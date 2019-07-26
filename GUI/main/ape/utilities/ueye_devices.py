import logging
from inspect import isclass

from qtpy.QtCore import Signal, Property, Slot

import Devices
from Devices import IDS_ueye

from .app_interface_object import AppInterfaceObject

logger = logging.getLogger('UEyeDevices')


class UEyeDevices(AppInterfaceObject):
    devicesChanged = Signal()

    def __init__(self, parent=None):
        super(UEyeDevices, self).__init__(parent)

        self._devices = []

    @Slot()
    def refresh(self):
        if not self._app_interface:
            logger.debug("Cannot refresh without an appInterface")
            return

        devices = []
        data = self._app_interface.app_image
        for name, device in data.get('devices', dict()).items():
            type_ = device['type'].value
            class_ = getattr(Devices, type_, None)
            if isclass(class_) and issubclass(class_, IDS_ueye):
                devices.append(name)

        self._devices = devices
        self.devicesChanged.emit()

    @Property(list, notify=devicesChanged)
    def devices(self):
        return self._devices
