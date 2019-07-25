import logging
from inspect import isclass

from qtpy.QtCore import QObject, Property, Signal, Slot, QUrl

import Procedures
import Project_Procedures
from Core import Procedure, Apparatus, Executor
from GUI.main.ape.base.helpers import value_to_str, str_to_value
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

        if device in ('Procedures', 'Project_Procedures', ''):
            if device == 'Procedures':
                module = Procedures
            elif device == 'Project_Procedures':
                module = Project_Procedures
            else:
                module = (
                    Procedures if procedure in dir(Procedures) else Project_Procedures
                )
            try:
                apparatus = Apparatus()
                executor = Executor()
                f = getattr(module, procedure)(apparatus, executor)
                return [
                    {'key': k, "value": value_to_str(v['value'])}
                    for k, v in f.requirements.items()
                ]
            except Exception as e:
                logger.warning(
                    f'Cannot fetch requirements of {device}_{procedure}: {str(e)}'
                )
                return []
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
                {'key': k, 'value': value_to_str(v)} for k, v in raw_reqs.items()
            ]
        self._proclist = raw_proclist
        self.proclistChanged.emit()

    @staticmethod
    def _convert_req_model_to_list(requirements):
        return {
            entry['key']: str_to_value(entry['value'])
            for entry in requirements
            if entry['value']
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

    @Slot(QUrl)
    def saveAs(self, url):
        if not self._gui_node:
            logger.warning('Cannot save without guiNode')
            return

        filename = url.toLocalFile()
        self._gui_node.executor.exportProclist(filename)

    @Slot(QUrl)
    def importFrom(self, url):
        if not self._gui_node:
            logger.warning('Cannot import without guiNode')
            return

        filename = url.toLocalFile()
        self._gui_node.executor.importProclist(filename)

    def _create_device(self, device_name, device_type, exec_address, rel_address):
        created = self._gui_node.executor.createDevice(
            device_name, device_type, exec_address, rel_address
        )
        if created:
            address = ['devices', device_name, 'type']
            if not self._gui_node.apparatus.checkAddress(address):
                self._gui_node.apparatus.createAppEntry(address)
            self._gui_node.apparatus.setValue(address, 'User_GUI')
            address = ['devices', device_name, 'address']
            if not self._gui_node.apparatus.checkAddress(address):
                self._gui_node.apparatus.createAppEntry(address)
            self._gui_node.apparatus.setValue(address, rel_address)
            address = ['devices', device_name, 'addresstype']
            if not self._gui_node.apparatus.checkAddress(address):
                self._gui_node.apparatus.createAppEntry(address)
            self._gui_node.apparatus.setValue(address, 'zmqNode')
            return True
        else:
            logger.error(f"Creating device {device_name} {device_type} failed")
            return False

    @Slot(str, str, result=bool)
    def createDevice(self, device_name, device_type):
        if not self._gui_node:
            logger.warning('Cannot create device without guiNode')
            return

        return self._create_device(device_name, device_type, 'procexec', 'procexec')

    @Slot(result=bool)
    def createUserDevice(self):
        if not self._gui_node:
            logger.warning('Cannot create use device without guiNode')
            return

        return self._create_device('User', 'User_GUI', 'procexec', 'gui')
