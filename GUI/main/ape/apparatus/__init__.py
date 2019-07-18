from qtpy.QtQml import qmlRegisterType

from .app_image_tree_model import AppImageTreeModel
from .app_interface import AppInterface
from .watchlist_model import WatchlistModel

MODULE_NAME = "ape.apparatus"


def register_types():
    qmlRegisterType(AppImageTreeModel, MODULE_NAME, 1, 0, AppImageTreeModel.__name__)
    qmlRegisterType(AppInterface, MODULE_NAME, 1, 0, AppInterface.__name__)
    qmlRegisterType(WatchlistModel, MODULE_NAME, 1, 0, WatchlistModel.__name__)
