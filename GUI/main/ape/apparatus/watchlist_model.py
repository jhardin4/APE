import logging

from qtpy.QtCore import QAbstractItemModel, Property, Signal, QModelIndex, Qt, Q_ENUMS

from .app_interface import AppInterface

logger = logging.getLogger('WatchlistTableModel')


class WatchlistModelRoles:
    KeyRole = Qt.UserRole
    ValueRole = Qt.UserRole + 1

    @staticmethod
    def role_names():
        return {
            WatchlistModelRoles.KeyRole: b'key',
            WatchlistModelRoles.ValueRole: b'value',
        }


class WatchlistModel(QAbstractItemModel, WatchlistModelRoles):

    Q_ENUMS(WatchlistModelRoles)

    appInterfaceChanged = Signal()

    def __init__(self, parent=None):
        super(WatchlistModel, self).__init__(parent)

        self._app_interface = None

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
            old_interface.watchedChanged.disconnect(self.modelReset)
            old_interface.itemUpdated.disconnect(self._on_item_updated)
        if new_interface:
            new_interface.watchedChanged.connect(self.modelReset)
            new_interface.itemUpdated.connect(self._on_item_updated)
            self.modelReset.emit()

    @property
    def _watched(self):
        if self._app_interface:
            return self._app_interface.watched
        else:
            return []

    def _on_item_updated(self, key):
        for i, item in enumerate(self._watched):
            if item.key == key:
                index = self.index(i, 0)
                self.dataChanged.emit(index, index)
                return

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        watched = self._watched
        row = index.row()
        if row >= len(watched):
            return None

        item = watched[row]
        switch = {
            Qt.DisplayRole: lambda: item.key,
            self.KeyRole: lambda: item.key,
            self.ValueRole: lambda: item.value,
        }

        data = switch.get(role, lambda: None)()
        return data

    def setData(self, index, value, role=Qt.EditRole):
        item = index.internalPointer()
        if role == self.ValueRole:
            item.value = value
            self._app_interface.setValue(item.key, value)
            changed = True
        else:
            changed = False

        if changed:
            self.dataChanged.emit(index, index, [role])
        return changed

    def roleNames(self):
        return self.role_names()

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent=QModelIndex()):
            return QModelIndex()

        item = self._app_interface.watched[row]
        return self.createIndex(row, column, item)

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def parent(self, index):
        return QModelIndex()

    def columnCount(self, _parent=QModelIndex()):
        return len(self.role_names())

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0

        return len(self._app_interface.watched)
