import logging
from collections import UserList

from qtpy.QtCore import (
    Property,
    Signal,
    Slot,
    Qt,
    Q_ENUMS,
    QAbstractItemModel,
    QModelIndex,
)

from .app_image_loader import AppImageLoader

logger = logging.getLogger('AppImageTreeModel')


class AppImageTreeModelRoles:
    NameRole = Qt.UserRole
    ValueRole = Qt.UserRole + 1

    @staticmethod
    def role_names():
        return {
            AppImageTreeModelRoles.NameRole: b'name',
            AppImageTreeModelRoles.ValueRole: b'value',
        }


class AppImageData(UserList):
    def __init__(self, name='', value='', parent=None):
        super(AppImageData, self).__init__()
        self.name = name
        self.value = value
        self.parent = parent

    def __str__(self):
        return f'{self.name}: {super().__str__()}'

    def __repr__(self):
        return f'{self.name}: {super().__repr__()}'


class AppImageTreeModel(QAbstractItemModel, AppImageTreeModelRoles):

    Q_ENUMS(AppImageTreeModelRoles)

    loaderChanged = Signal()

    def __init__(self, parent=None):
        super(AppImageTreeModel, self).__init__(parent)

        self._app_image = None
        self._data = AppImageData()
        self._loader = None

    @Property(AppImageLoader, notify=loaderChanged)
    def loader(self):
        return self._loader

    @loader.setter
    def loader(self, new_loader):
        if new_loader == self._loader:
            return
        old_loader = self._loader
        self._loader = new_loader
        self.loaderChanged.emit()

        if old_loader:
            old_loader.dataChanged.disconnect(self.refresh)
        if new_loader:
            new_loader.dataChanged.connect(self.refresh)

    @Slot()
    def refresh(self):
        if not self._loader:
            logger.warning('cannot refresh without a loader')
            return

        app_image = self._loader.data

        def create_data_item(key, value):
            item = AppImageData(name=key)
            if isinstance(value, dict):
                for k, v in value.items():
                    child = create_data_item(k, v)
                    child.parent = item
                    item.append(child)
            elif isinstance(value, list):
                item.value = ''
            else:
                item.value = value
            return item

        self.beginResetModel()
        self._data = create_data_item('root', app_image)
        self.endResetModel()

    def data(self, index, role):
        if not index.isValid():
            return None

        item = index.internalPointer()
        switch = {
            Qt.DisplayRole: lambda: item.name,
            self.NameRole: lambda: item.name,
            self.ValueRole: lambda: str(item.value),
        }

        data = switch.get(role, lambda: None)()
        return data

    def roleNames(self):
        return self.role_names()

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, _section, orientation, role=Qt.DisplayRole):
        if not orientation == Qt.Horizontal:
            return None

        return self.role_names().get(role, '').title()

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

        if parent_item == self._data:
            return QModelIndex()

        row = parent_item.parent.index(parent_item)
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
