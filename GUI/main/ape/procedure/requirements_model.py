# -*- coding: utf-8 -*-
from collections import OrderedDict

from qtpy.QtCore import Signal, Property, QAbstractItemModel, Qt, QModelIndex, Q_ENUMS


class RequirementsModelRoles:
    KeyRole = Qt.UserRole
    ValueRole = Qt.UserRole + 1

    @staticmethod
    def role_names():
        return {
            RequirementsModelRoles.KeyRole: b'key',
            RequirementsModelRoles.ValueRole: b'value',
        }


class RequirementsModel(QAbstractItemModel, RequirementsModelRoles):

    Q_ENUMS(RequirementsModelRoles)

    requirementsChanged = Signal()

    def __init__(self, parent=None):
        super(RequirementsModel, self).__init__(parent)

        self._requirements = OrderedDict()

        self.requirementsChanged.connect(self.modelReset)

    @Property(OrderedDict, notify=requirementsChanged)
    def requirements(self):
        return self._requirements

    @requirements.setter
    def requirements(self, value):
        if value is self._requirements:
            return
        self._requirements = value
        self.requirementsChanged.emit()

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        key = list(self._requirements.keys())[index.row()]
        switch = {
            Qt.DisplayRole: lambda: key,
            self.KeyRole: lambda: key,
            self.ValueRole: lambda: self._requirements[key],
        }

        data = switch.get(role, lambda: None)()
        return data

    def roleNames(self):
        return self.role_names()

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        return self.createIndex(row, column)

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, _section, orientation, role=Qt.DisplayRole):
        if not orientation == Qt.Horizontal:
            return None

        return self.role_names().get(role, '').title()

    def parent(self, index):
        return QModelIndex()

    def columnCount(self, _parent=QModelIndex()):
        return len(self.role_names())

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0

        return len(self._requirements)
