from qtpy.QtQml import qmlRegisterType

from .app_image_tree_model import AppImageTreeModel
from .app_image_loader import AppImageLoader

MODULE_NAME = "ape.apparatus"


def register_types():
    qmlRegisterType(AppImageTreeModel, MODULE_NAME, 1, 0, AppImageTreeModel.__name__)
    qmlRegisterType(AppImageLoader, MODULE_NAME, 1, 0, AppImageLoader.__name__)
