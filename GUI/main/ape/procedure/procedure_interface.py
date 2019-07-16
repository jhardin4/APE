import logging

from qtpy.QtCore import QObject, Property, Signal, Slot

import Procedures
from ..nodes import GuiNode

logger = logging.getLogger('ProcedureInterface')


class ProcedureInterface(QObject):
    _gui_node: GuiNode
    guiNodeChanged = Signal()
    eprocsChanged = Signal()

    def __init__(self, parent=None):
        super(ProcedureInterface, self).__init__(parent)

        self._gui_node = None
        self._eprocs = {}

    @Property(GuiNode, notify=guiNodeChanged)
    def guiNode(self):
        return self._gui_node

    @guiNode.setter
    def guiNode(self, value):
        if value == self._gui_node:
            return
        self._gui_node = value
        self.guiNodeChanged.emit()

    @property
    def eprocs(self):
        return self._eprocs

    @Slot()
    def refreshEprocs(self):
        if not self._gui_node:
            logger.warning('Cannot fetch eprocs without guiNode')
            return

        logger.debug('fetching EProcs')
        epl_dict = {}
        epl = self._gui_node.executor.getDevices('procexec')
        for device in epl:
            eprocs = self._gui_node.executor.getEprocs(device, 'procexec')
            epl_dict[device] = eprocs
        logger.debug(f'Eprocs fetched {epl_dict}')
        self._eprocs = epl_dict
        self.eprocsChanged.emit()

    @Slot(str, str, result=list)
    def getRequirements(self, device, procedure):
        if not self._gui_node:
            logger.warning('Cannot fetch requirements without guiNode')
            return

        name = f'{device}_{procedure}'
        if name in dir(Procedures):
            f = getattr(Procedures, name)(
                self._gui_node.apparatus, self._gui_node.executor
            )
            return [{'key': k, "value": v} for k, v in f.requirements.items()]
        else:
            reqs = self._gui_node.executor.getRequirements(
                device, procedure, 'procexec'
            )
            return [{'key': k, 'value': ''} for k in reqs]

    @Slot(str, str, list)
    def do(self, device, procedure, requirements):
        if not self._gui_node:
            logger.warning('Cannot do procedure with guiNode')
            return

        reqs = {entry['key']: entry['value'] for entry in requirements}
        logger.debug(f'do procedure {device}_{procedure}, reqs: {reqs}')
        self._gui_node.executor.do(device, procedure, reqs)
        logger.debug('done')
