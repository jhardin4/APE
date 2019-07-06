import logging

from qtpy.QtCore import (
    Property,
    Signal,
    Slot,
    Qt,
    Q_ENUMS,
    QAbstractItemModel,
    QModelIndex,
)

from GUI.main.ape.nodes import GuiNode

logger = logging.getLogger('AppImageTreeModel')


class AppImageTreeModelRoles(object):
    NameRole = Qt.UserRole
    ValueRole = Qt.UserRole + 1

    @staticmethod
    def role_names():
        return {
            AppImageTreeModelRoles.NameRole: 'name',
            AppImageTreeModelRoles.ValueRole: 'value',
        }


class AppImageData(list):
    def __init__(self, name='', value=None, parent=None):
        super(AppImageData, self).__init__()
        self.name = name
        self.value = value
        self.parent = parent


class AppImageTreeModel(QAbstractItemModel, AppImageTreeModelRoles):
    guiNodeChanged = Signal()

    Q_ENUMS(AppImageTreeModelRoles)

    def __init__(self, parent=None):
        super(AppImageTreeModel, self).__init__(parent)

        self._gui_node = None
        self._app_image = None
        self._data = AppImageData()

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
            logger.warning('cannot refresh without a gui node')
            return

        self._app_image = self._gui_node.apparatus.serialClone()

        def create_data_item(key, value):
            item = AppImageData(name=key)
            if isinstance(value, dict):
                for k, v in value.items():
                    child = create_data_item(k, v)
                    child.parent = item
                    item.append(child)
            else:
                item.value = str(value)
            return item

        self._data = create_data_item('root', self._app_image)

    def data(self, index, role):
        if not index.isValid():
            return None

        item = index.internalPointer()
        switch = {
            Qt.DisplayRole: lambda: item.name,
            self.NameRole: lambda: item.name,
            self.ValueRole: lambda: item.value,
        }

        return switch.get(role, lambda: None)()

    def roleNames(self):
        return self.role_names()

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def _get_item(self, index):
        if index and index.isValid():
            item = index.internalPointer()
            if item:
                return item

        return self._data

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        parent_item = self._get_item(parent)
        try:
            child_item = parent_item[row]
        except IndexError:
            return QModelIndex()
        else:
            return self.createIndex(row, column, child_item)

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent

        if parent_item is self._data:
            return QModelIndex()

        row = parent_item.parent.children.index(parent_item)
        return self.createIndex(row, 0, parent_item)

    def columnCount(self, _parent=QModelIndex()):
        return len(self.role_names())

    def rowCount(self, parent=QModelIndex()):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent_item = self._data
        else:
            parent_item = parent.internalPointer()

        return len(parent_item) if parent_item else 0
