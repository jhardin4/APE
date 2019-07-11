import logging
from collections import OrderedDict
from qtpy.QtCore import QObject, Signal, Property, Slot

from ..nodes import GuiNode

logger = logging.getLogger('AppInterface')


class AppImageData(OrderedDict):
    def __init__(self, name='', value='', parent=None):
        super(AppImageData, self).__init__()
        self.name = name
        self.value = value
        self.parent = parent

    def __str__(self):
        return f'{self.name}: {super().__str__()}'

    def __repr__(self):
        return f'{self.name}: {super().__repr__()}'

    @staticmethod
    def from_dict(dict_, name):
        def create_data_item(key, value):
            item = AppImageData(name=key)
            if isinstance(value, dict):
                for k, v in value.items():
                    child = create_data_item(k, v)
                    child.parent = item
                    item[k] = child
            else:
                item.value = value
            return item

        return create_data_item(name, dict_)


class AppImageDataWalker:
    """
    The walker performs a breath first search on the given item. The behavior
    can be changed by supplying the optional dfs parameter to depth first search.
    """

    def __init__(self, item, dfs=False):
        self.item = item
        self.dfs = dfs

    @staticmethod
    def _walk(item, dfs):
        # if item is None:
        #     return
        if not dfs:
            yield item
        for child in item.values():
            for walked in AppImageDataWalker._walk(child, dfs):
                yield walked
        if dfs:
            yield item

    def __iter__(self):
        return AppImageDataWalker._walk(self.item, self.dfs)


class AppInterface(QObject):

    _gui_node: GuiNode
    guiNodeChanged = Signal()
    appImageChanged = Signal()

    def __init__(self, parent=None):
        super(AppInterface, self).__init__(parent)

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
        data = self._gui_node.apparatus.serialClone()
        self._app_image = AppImageData.from_dict(data, 'root')

        logger.debug(f'serial clone completed {self._app_image}')

        self.appImageChanged.emit()

    @property
    def app_image(self):
        return self._app_image

    @Slot(str, str, result=int)
    def findAndReplace(self, find, replace):
        count = 0
        for item in AppImageDataWalker(self._app_image):
            if item.value == find:
                item.value = replace
                count += 1
        self.appImageChanged.emit()
        return count

    @Slot(bool)
    def connectAll(self, simulation):
        self._gui_node.apparatus.Connect_All(simulation=simulation)

        for device in self._app_image['devices'].keys():
            self._app_image['devices'][device]['Connected'].value = 'True'
        self.appImageChanged.emit()

    @Slot()
    def disconnectAll(self):
        self._gui_node.apparatus.Disconnect_All()
        for device in self._app_image['devices'].keys():
            self._app_image['devices'][device]['Connected'].value = 'False'
        self.appImageChanged.emit()
