import logging

from qtpy.QtCore import Property, Signal, Slot, QModelIndex
from qtpy.QtGui import QStandardItemModel, QStandardItem

from ..apparatus.app_interface import AppInterface

logger = logging.getLogger('ProcedureModel')


class ProcedureModel(QStandardItemModel):
    _app_interface: AppInterface
    appInterfaceChanged = Signal()

    def __init__(self, parent=None):
        super(ProcedureModel, self).__init__(parent)

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
            old_interface.eprocsChanged.disconnect(self.refresh)
        if new_interface:
            new_interface.eprocsChanged.connect(self.refresh)
            self.refresh()

    @Slot()
    def refresh(self):
        self.clear()

        if not self._app_interface:
            logger.warning('cannot refresh without an appInterface')
            return

        eprocs = self._app_interface.eprocs
        for device in eprocs.keys():
            device_item = QStandardItem(device)
            self.appendRow(device_item)
            for eproc in eprocs[device]:
                eproc_item = QStandardItem(eproc)
                device_item.appendRow(eproc_item)

    @Slot(QModelIndex, result=list)
    def getProcedureName(self, index):
        if not index.isValid():
            return []

        if not index.parent().isValid():
            return []

        device = self.data(index.parent())
        proc = self.data(index)

        return [device, proc]
