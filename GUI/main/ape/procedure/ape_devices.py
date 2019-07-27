from inspect import isclass

from qtpy.QtCore import QObject, Property

import Devices


class ApeDevices(QObject):
    def __init__(self, parent=None):
        super(ApeDevices, self).__init__(parent)

    @Property(list, constant=True)
    def devices(self):
        return [name for name in dir(Devices) if isclass(getattr(Devices, name))]
