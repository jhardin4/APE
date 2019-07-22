from qtpy.QtQml import qmlRegisterType

from .motion_devices import MotionDevices

MODULE_NAME = "ape.utilities"


def register_types():
    qmlRegisterType(MotionDevices, MODULE_NAME, 1, 0, MotionDevices.__name__)
