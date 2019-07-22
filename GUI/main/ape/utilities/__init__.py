from qtpy.QtQml import qmlRegisterType

from .motion_devices import MotionDevices
from .ueye_view import UEyeView

MODULE_NAME = "ape.utilities"


def register_types():
    qmlRegisterType(MotionDevices, MODULE_NAME, 1, 0, MotionDevices.__name__)
    qmlRegisterType(UEyeView, MODULE_NAME, 1, 0, UEyeView.__name__)
