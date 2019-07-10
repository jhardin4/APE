import logging
from qtpy.QtCore import QObject, Signal, Property, Slot

from ..nodes import GuiNode

logger = logging.getLogger('AppImageLoader')


class AppImageLoader(QObject):

    guiNodeChanged = Signal()
    dataChanged = Signal()

    def __init__(self, parent=None):
        super(AppImageLoader, self).__init__(parent)

        print('created', id(self), parent)
        self._gui_node = None
        self._app_image = {}

    @Property(GuiNode, notify=guiNodeChanged)
    def guiNode(self):
        return self._gui_node

    @guiNode.setter
    def guiNode(self, value):
        if value == self._gui_node:
            return
        self._gui_node = value
        self.guiNodeChanged.emit()

    @Slot()
    def refresh(self):
        if not self._gui_node:
            logger.warning('Cannot refresh without guiNode')

        logger.debug('starting serial clone')
        self._app_image = self._gui_node.apparatus.serialClone()
        logger.debug(f'serial clone completed {self._app_image}')

        self.dataChanged.emit()

    @property
    def data(self):
        return self._app_image
