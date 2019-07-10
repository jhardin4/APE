from qtpy.QtQml import qmlRegisterType

from .gui_node import GuiNode

MODULE_NAME = "ape.nodes"


def register_types():
    qmlRegisterType(GuiNode, MODULE_NAME, 1, 0, GuiNode.__name__)
