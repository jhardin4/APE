from qtpy.QtQml import qmlRegisterType

from .motion_devices import MotionDevices
from .ueye_view import UEyeView
from .toolpath_plot import ToolPathPlot
from .ueye_devices import UEyeDevices

MODULE_NAME = "ape.utilities"


def register_types():
    qmlRegisterType(MotionDevices, MODULE_NAME, 1, 0, MotionDevices.__name__)
    qmlRegisterType(UEyeView, MODULE_NAME, 1, 0, UEyeView.__name__)
    qmlRegisterType(ToolPathPlot, MODULE_NAME, 1, 0, ToolPathPlot.__name__)
    qmlRegisterType(UEyeDevices, MODULE_NAME, 1, 0, UEyeDevices.__name__)
