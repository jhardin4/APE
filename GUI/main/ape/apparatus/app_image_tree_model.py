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

from ..base.helpers import str_to_value, value_to_str
from .app_interface import AppInterface
from .app_image_data import AppImageData

logger = logging.getLogger('AppImageTreeModel')


class AppImageTreeModelRoles:
    NameRole = Qt.UserRole
    ValueRole = Qt.UserRole + 1
    WatchRole = Qt.UserRole + 2
    KeyRole = Qt.UserRole + 3

    @staticmethod
    def role_names():
        return {
            AppImageTreeModelRoles.NameRole: b'name',
            AppImageTreeModelRoles.ValueRole: b'value',
            AppImageTreeModelRoles.WatchRole: b'watch',
            AppImageTreeModelRoles.KeyRole: b'key',
        }


class AppImageTreeModel(QAbstractItemModel, AppImageTreeModelRoles):

    Q_ENUMS(AppImageTreeModelRoles)

    appInterfaceChanged = Signal()

    def __init__(self, parent=None):
        super(AppImageTreeModel, self).__init__(parent)

        self._app_image = None
        self._data = AppImageData()
        self._app_interface = None
        self._watched = []

    @Property(AppInterface, notify=appInterfaceChanged)
    def appInterface(self):
        return self._app_interface

    @appInterface.setter
    def appInterface(self, new_interface):
        if new_interface == self._app_interface:
            return
        old_interface = self._app_interface
        self._app_interface = new_interface
        self.appInterfaceChanged.emit()

        if old_interface:
            old_interface.appImageChanged.disconnect(self.refresh)
            old_interface.itemUpdated.disconnect(self._on_item_updated)
        if new_interface:
            new_interface.appImageChanged.connect(self.refresh)
            new_interface.itemUpdated.connect(self._on_item_updated)
            self.refresh()

    def _on_item_updated(self, key):
        levels = key.split('/')
        item = self._data
        for level in levels:
            item = item.get(level, None)
            if item is None:
                return

        if item.parent is None:
            row = 0
        else:
            row = list(item.parent.values()).index(item)
        index = self.createIndex(row, 0, item)
        self.dataChanged.emit(index, index)

    @Slot()
    def refresh(self):
        if not self._app_interface:
            logger.warning('cannot refresh without an appInterface')
            return

        self.beginResetModel()
        self._data = self._app_interface.app_image
        self.endResetModel()

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        item = index.internalPointer()
        switch = {
            Qt.DisplayRole: lambda: item.name,
            self.NameRole: lambda: item.name,
            self.ValueRole: lambda: value_to_str(item.value),
            self.WatchRole: lambda: item.watch,
            self.KeyRole: lambda: item.key,
        }

        data = switch.get(role, lambda: None)()
        return data

    def setData(self, index, value, role=Qt.EditRole):
        item = index.internalPointer()
        if role in (Qt.EditRole, self.NameRole):
            item.name = value
            changed = True
        elif role == self.ValueRole:
            new_value = str_to_value(value, item.value)
            if new_value is None:
                logger.error(f'Cannot convert value {item.key} {value}')
                changed = False
            else:
                item.value = new_value
                self._app_interface.setValue(item.key, new_value)
                changed = True
        elif role == self.WatchRole:
            if value:
                self._app_interface.append_watched(item)
            else:
                self._app_interface.remove_watched(item)
            changed = True
        else:
            changed = False

        if changed:
            self.dataChanged.emit(index, index, [role])
        return changed

    def roleNames(self):
        return self.role_names()

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        item = index.internalPointer()
        if not index.parent().isValid() and item.name not in ('proclog', 'eproclist'):
            flags |= Qt.ItemIsTristate
        elif len(item) == 0:
            flags |= Qt.ItemIsEditable
        elif index.parent().isValid():
            flags |= Qt.ItemIsTristate

        return flags

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
            child_item = list(parent_item.values())[row]
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

        row = list(parent_item.parent.values()).index(parent_item)
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
