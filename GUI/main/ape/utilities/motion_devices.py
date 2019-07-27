import logging
from inspect import isclass

from qtpy.QtCore import Signal, Property, Slot

import Devices
from Devices import Motion

from .app_interface_object import AppInterfaceObject

logger = logging.getLogger('MotionDevices')


class MotionDevices(AppInterfaceObject):
    devicesChanged = Signal()

    def __init__(self, parent=None):
        super(MotionDevices, self).__init__(parent)

        self._devices = []

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
