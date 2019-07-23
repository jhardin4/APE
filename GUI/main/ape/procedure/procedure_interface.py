import logging
from inspect import isclass

from qtpy.QtCore import QObject, Property, Signal, Slot

import Procedures
import Project_Procedures
from Core import Procedure
from ..nodes import GuiNode

logger = logging.getLogger('ProcedureInterface')


class ProcedureInterface(QObject):
    _gui_node: GuiNode
    guiNodeChanged = Signal()
    eprocsChanged = Signal()
    proclistChanged = Signal()

    def __init__(self, parent=None):
        super(ProcedureInterface, self).__init__(parent)

        self._gui_node = None
        self._eprocs = {}
        self._proclist = []

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

    @Property(list, notify=proclistChanged)
    def proclist(self):
        return self._proclist

    @Slot()
    def refreshEprocs(self):
        if not self._gui_node:
            logger.warning('Cannot fetch eprocs without guiNode')
            return

        def procs_from_module(module):
            procs = []
            for name in dir(module):
                proc = getattr(module, name)
                if isclass(proc) and issubclass(proc, Procedure):
                    procs.append(name)
            return procs

        logger.debug('fetching EProcs')
        epl_dict = {
            'Procedures': procs_from_module(Procedures),
            'Project_Procedures': procs_from_module(Project_Procedures),
        }

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

        if device in ('Procedures', 'Project_Procedures'):
            module = Procedures if device == 'Procedures' else Project_Procedures
            f = getattr(module, procedure)(
                self._gui_node.apparatus, self._gui_node.executor
            )
            return [
                {'key': k, "value": str(v['value'])} for k, v in f.requirements.items()
            ]
        else:
            reqs = self._gui_node.executor.getRequirements(
                device, procedure, 'procexec'
            )
            return [{'key': k, 'value': ''} for k in reqs]

    @Slot()
    def refreshProclist(self):
        if not self._gui_node:
            logger.warning('Cannot refresh proclist without guiNode')
            return

        logger.debug('fetching proclist')
        raw_proclist = self._gui_node.executor.getProclist()
        logger.debug(f'proclist updated {raw_proclist}')
        for entry in raw_proclist:
            if entry['device']:
                entry['name'] = f'{entry["device"]}_{entry["procedure"]}'
            else:
                entry['name'] = entry['procedure']
            raw_reqs = entry["requirements"]
            entry["requirements"] = [
                {'key': k, 'value': v} for k, v in raw_reqs.items()
            ]
        self._proclist = raw_proclist
        self.proclistChanged.emit()

    @staticmethod
    def _convert_req_model_to_list(requirements):
        return {
            entry['key']: entry['value'] for entry in requirements if entry['value']
        }

    @Slot(str, str, list)
    def addProcedure(self, device, procedure, requirements):
        if not self._gui_node:
            logger.warning('Cannot add requirements without guiNode')
            return

        if device in ('Procedures', 'Project_Procedures'):
            device = ''

        reqs = self._convert_req_model_to_list(requirements)
        self._gui_node.executor.insertProc(
            index=-1, device=device, procedure=procedure, requirements=reqs
        )

    @Slot(int)
    def removeProcedure(self, index):
        if not self._gui_node:
            logger.warning('Cannot remove procedure without guiNode')
            return

        if 0 <= index < len(self._proclist):
            self._gui_node.executor.removeProc(index=index)

    @Slot(int)
    def moveProcedureUp(self, index):
        if not self._gui_node:
            logger.warning('Cannot move procedure without guiNode')
            return

        if 0 < index < len(self._proclist):
            self._gui_node.executor.swapProcs(index - 1, index)

    @Slot(int)
    def moveProcedureDown(self, index):
        if not self._gui_node:
            logger.warning('Cannot move procedure without guiNode')
            return

        if 0 <= index < (len(self._proclist) - 1):
            self._gui_node.executor.swapProcs(index + 1, index)

    @Slot(int, list)
    def updateProcedure(self, index, requirements):
        if not self._gui_node:
            logger.warning('Cannot update procedure without guiNode')
            return

        if 0 <= index < len(self._proclist):
            reqs = self._convert_req_model_to_list(requirements)
            self._gui_node.executor.updateProc(index, reqs)

    @Slot()
    def clearProclist(self):
        if not self._gui_node:
            logger.warning('Cannot move procedure without guiNode')
            return

        self._gui_node.executor.clearProclist()

    @Slot(int)
    def doProcedure(self, index):
        if not self._gui_node:
            logger.warning('Cannot do procedure without guiNode')
            return

        if 0 <= index < len(self._proclist):
            self._gui_node.executor.doProc(index)

    @Slot()
    def doProclist(self):
        if not self._gui_node:
            logger.warning('Cannot do proclist without guiNode')
            return

        self._gui_node.executor.doProclist()

    @Slot(str, str, list)
    def do(self, device, procedure, requirements):
        if not self._gui_node:
            logger.warning('Cannot do procedure without guiNode')
            return

        if device in ('Procedures', 'Project_Procedures'):
            device = ''

        reqs = self._convert_req_model_to_list(requirements)
        logger.debug(f'do procedure {device}_{procedure}, reqs: {reqs}')
        self._gui_node.executor.do(device, procedure, reqs)
        logger.debug('done')
