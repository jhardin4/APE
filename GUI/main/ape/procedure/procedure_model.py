import logging

from qtpy.QtCore import Property, Signal, Slot, QModelIndex
from qtpy.QtGui import QStandardItemModel, QStandardItem

from .procedure_interface import ProcedureInterface

logger = logging.getLogger('ProcedureModel')


class ProcedureModel(QStandardItemModel):
    _proc_interface: ProcedureInterface
    procInterfaceChanged = Signal()

    def __init__(self, parent=None):
        super(ProcedureModel, self).__init__(parent)

        self._proc_interface = None

    @Property(ProcedureInterface, notify=procInterfaceChanged)
    def procInterface(self):
        return self._proc_interface

    @procInterface.setter
    def procInterface(self, new_interface):
        if new_interface == self._proc_interface:
            return
        old_interface = self._proc_interface
        self._proc_interface = new_interface
        self.procInterfaceChanged.emit()

        if old_interface:
            old_interface.eprocsChanged.disconnect(self.refresh)
        if new_interface:
            new_interface.eprocsChanged.connect(self.refresh)
            self.refresh()

    @Slot()
    def refresh(self):
        self.clear()

        if not self._proc_interface:
            logger.warning('cannot refresh without a procInterface')
            return

        eprocs = self._proc_interface.eprocs
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
