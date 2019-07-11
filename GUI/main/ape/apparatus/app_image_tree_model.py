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

from .app_interface import AppInterface, AppImageData

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


class AppImageTreeModel(QAbstractItemModel, AppImageTreeModelRoles):

    Q_ENUMS(AppImageTreeModelRoles)

    appInterfaceChanged = Signal()

    def __init__(self, parent=None):
        super(AppImageTreeModel, self).__init__(parent)

        self._app_image = None
        self._data = AppImageData()
        self._appInterface = None

    @Property(AppInterface, notify=appInterfaceChanged)
    def appInterface(self):
        return self._appInterface

    @appInterface.setter
    def appInterface(self, new_interface):
        if new_interface == self._appInterface:
            return
        old_interface = self._appInterface
        self._appInterface = new_interface
        self.appInterfaceChanged.emit()

        if old_interface:
            old_interface.appImageChanged.disconnect(self.refresh)
        if new_interface:
            new_interface.appImageChanged.connect(self.refresh)

    @Slot()
    def refresh(self):
        if not self._appInterface:
            logger.warning('cannot refresh without an appInterface')
            return

        self.beginResetModel()
        self._data = self._appInterface.app_image
        self.endResetModel()

    def data(self, index, role=Qt.DisplayRole):
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
