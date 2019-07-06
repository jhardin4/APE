from qtpy.QtQml import qmlRegisterType

from .node import AppaNode, ProcExecNode
from .gui_node import GuiNode
from .launcher import Launcher

MODULE_NAME = "ape.nodes"


def register_types():
    qmlRegisterType(AppaNode, MODULE_NAME, 1, 0, AppaNode.__name__)
    qmlRegisterType(ProcExecNode, MODULE_NAME, 1, 0, ProcExecNode.__name__)
    qmlRegisterType(Launcher, MODULE_NAME, 1, 0, Launcher.__name__)
    qmlRegisterType(GuiNode, MODULE_NAME, 1, 0, GuiNode.__name__)
