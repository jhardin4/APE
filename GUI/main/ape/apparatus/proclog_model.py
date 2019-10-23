import logging
from collections import deque

from qtpy.QtGui import QStandardItemModel, QStandardItem
from qtpy.QtCore import Property, Signal, Slot, Qt, Q_ENUMS

from .app_interface import AppInterface

logger = logging.getLogger('ProclogModel')


class ProclogModelRoles:
    NameRole = Qt.DisplayRole
    IdRole = Qt.UserRole + 1
    IsProcedureRole = Qt.UserRole + 2
    ValueRole = Qt.UserRole + 3

    @staticmethod
    def role_names():
        return {
            ProclogModelRoles.NameRole: b'name',
            ProclogModelRoles.IdRole: b'id',
            ProclogModelRoles.IsProcedureRole: b'isProcedure',
            ProclogModelRoles.ValueRole: b'value',
        }


class ProclogModel(QStandardItemModel, ProclogModelRoles):

    Q_ENUMS(ProclogModelRoles)

    appInterfaceChanged = Signal()

    def __init__(self, parent=None):
        super(ProclogModel, self).__init__(parent)
        self._app_interface = None
        self.setSortRole(self.IdRole)

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
            old_interface.proclogChanged.disconnect(self.refresh)
        if new_interface:
            new_interface.proclogChanged.connect(self.refresh)
            self.refresh()

    @Slot()
    def refresh(self):
        self.clear()

        if not self._app_interface:
            logger.warning('cannot refresh without an appInterface')
            return

        proclog = self._app_interface.proclog
        previous_level = 0
        item_stack = deque([self])
        for i, log in enumerate(proclog):
            level = 0
            name = ''
            info = {}
            for item in log:
                if item == '->':
                    level += 1
                else:
                    name = item['name']
                    info = item['information']
            item = QStandardItem(name)
            item.setData(True, self.IsProcedureRole)
            item.setData('', self.ValueRole)
            item.setData(i + 1, self.IdRole)
            if isinstance(info, dict) and len(info):
                data_item = QStandardItem(self.tr('data'))
                data_item.setData(False, self.IsProcedureRole)
                data_item.setData('', self.ValueRole)
                for k, v in info.items():
                    entry_item = QStandardItem(k)
                    if isinstance(v, dict) and 'address' in v and 'value' in v:
                        value_item = QStandardItem('value')
                        value_item.setData(str(v['value']), self.ValueRole)
                        value_item.setData(False, self.IsProcedureRole)
                        entry_item.appendRow(value_item)
                        value_item = QStandardItem('address')
                        value_item.setData(str(v['address']), self.ValueRole)
                        value_item.setData(False, self.IsProcedureRole)
                        entry_item.appendRow(value_item)
                        value = ''
                    else:
                        value = str(v)
                    entry_item.setData(value, self.ValueRole)
                    entry_item.setData(False, self.IsProcedureRole)
                    data_item.appendRow(entry_item)
                item.appendRow(data_item)
            elif isinstance(info, str):
                data_item = QStandardItem(self.tr('info'))
                data_item.setData(False, self.IsProcedureRole)
                data_item.setData(info, self.ValueRole)
                item.appendRow(data_item)

            if level > previous_level:
                previous_level = level
            elif level == previous_level:
                item_stack.pop()
            else:
                item_stack.pop()
                while previous_level > level and previous_level > 0:
                    item_stack.pop()
                    previous_level -= 1
            item_stack[-1].appendRow(item)
            item_stack.append(item)

    def roleNames(self):
        return self.role_names()
