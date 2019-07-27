import os

from qtpy.QtCore import QObject, QUrl, Property

MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
RESOURCE_PATH = os.path.realpath(os.path.join(MODULE_PATH, '../../res'))
ICON_PATH = os.path.join(RESOURCE_PATH, 'icons')
FONT_PATH = os.path.join(RESOURCE_PATH, 'fonts')


class ResourcePaths(QObject):
    _engine = None

    def __init__(self, parent=None):
        super(ResourcePaths, self).__init__(parent)

        self._icon_path = QUrl.fromLocalFile(ICON_PATH)
        self._font_path = QUrl.fromLocalFile(FONT_PATH)
        self._root_path = QUrl.fromLocalFile(os.getcwd())

    @staticmethod
    def qml_singleton_provider(engine, _):
        ResourcePaths._engine = engine

        return ResourcePaths()

    @Property(QUrl, constant=True)
    def iconPath(self):
        return self._icon_path

    @Property(QUrl, constant=True)
    def fontPath(self):
        return self._font_path

    @Property(QUrl, constant=True)
    def rootPath(self):
        return self._root_path
