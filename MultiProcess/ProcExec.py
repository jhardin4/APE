import json
import sys
from importlib import reload
from inspect import isclass
from types import ModuleType
from uuid import uuid4

import Core
import Procedures
import Project_Procedures
from MultiProcess.zmqNode import zmqNode
from MultiProcess import APE_Interfaces


class ProcExec:
    def __init__(self, PE2L_address, PE2A_address, PE2G_address):
        # Create the node and set its target to ProcExec
        self.node = zmqNode('procexec')
        self.node.target = self
        self.node.logging = True
        self.loopBlocks = {}
        # creates an executor
        self.executor = Core.Executor(self.node)
        # Dictionary of all instances of Procedures and their associated requirements
        # {'uuid':{
        #     'proc': <Instance>,
        #     'device': <name of device>,
        #     'procedure': <name of procedure>,
        #     'requirements': <list of requirements>
        #     }}
        self.procedures = {}
        # List of the procedures in the order they are to be done
        # [
        # {'uuid': <procedure instance uuid>, 'requirements': <list of requirements>},
        # ...]
        self.proclist = []
        # Create an interface for the apparatus and assign it to the executor
        self.apparatus = APE_Interfaces.ApparatusInterface(self.node)
        # connect to launcher, apparatus, and gui process
        self.connect2L(PE2L_address)
        self.connect2A(PE2A_address)
        self.connect2G(PE2G_address)
        self.node.start_listening()

    def connect2L(self, PE2L_address):
        """
        connects to G as server, L and A as client
        """
        self.node.connect('launcher', PE2L_address)

    def connect2A(self, PE2A_address):
        self.node.connect('appa', PE2A_address)

    def connect2G(self, PE2G_address):
        self.node.connect('gui', PE2G_address, server=True)

    def _create_procedure(self, device, procedure):
        # Handle 'normal' procedures
        if device == '':
            raw_proc = getattr(Procedures, procedure, None)
            if raw_proc is None:
                raw_proc = getattr(Project_Procedures, procedure)
            proc = raw_proc(self.apparatus, self.executor)
        # Handle device procedures
        else:
            dev_address = self.apparatus.getValue(['devices', device, 'address'])

            class DevProc(Core.Procedure):
                def Prepare(self):
                    self.name = procedure
                    self.requirements = {
                        key: {'source': 'apparatus', 'address': '', 'value': ''}
                        for key in self.executor.getRequirements(
                            device, procedure, dev_address
                        )
                    }

                def Do(self, values=None):
                    if values is None:
                        values = {}
                    self.GetRequirements(values)
                    # self.CheckRequirements()
                    details = {
                        req: item['value'] for req, item in self.requirements.items()
                    }
                    self.DoEproc(device, procedure, details)

            proc = DevProc(self.apparatus, self.executor)

        return proc

    def _resolve_value(self, value, eproc):
        print('resolving')
        # reference syntax
        if value.startswith('@'):
            return self.apparatus.getValue(value[1:].split('/'))

        # procedure syntax
        elif value.startswith('!') and not eproc:
            print(value)
            print(str(self.procedures.keys()))
            try:
                for proc in self.procedures.items():
                    print(value[1:] + 'compared to ' + proc['procedure'])
                    if value[1:] == proc['procedure']:
                        print(str(type(proc['proc'])))
                        return proc['proc']
            except AttributeError:
                pass
            return None
        else:
            return value

    def _resolve_requirements(self, reqs, eproc):
        filled = reqs.copy()
        for name, value in filled.items():
            if isinstance(value, str):
                real_value = self._resolve_value(value, eproc)
                filled[name] = real_value
        return filled

    def getProcedures(self):
        """
        Returns all instantiated procedures.
        """
        return [
            dict({k: v for k, v in proc.items() if k != 'proc'}, uuid=uuid)
            for uuid, proc in self.procedures.items()
        ]

    def clearProcedures(self):
        """
        Deletes all instantiated procedures.
        """
        self.procedures.clear()
        self.clearProclist()

    def reloadProcedures(self):
        """
        Reloads all local procedure instances
        """
        for item in self.procedures.values():
            del item['proc']

        def deep_reload(module):
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                if isclass(attribute):
                    reload(sys.modules[attribute.__module__])
                elif type(attribute) is ModuleType:
                    reload(attribute)
            reload(module)

        deep_reload(Procedures)
        deep_reload(Project_Procedures)

        for item in self.procedures.values():
            proc = self._create_procedure(item['device'], item['procedure'])
            item['proc'] = proc

    def createProcedure(self, device, procedure, uuid=None):
        """
        Instantiates a new procedure.
        :param device: Name of the device.
        :param procedure: Name of the procedure.
        :param uuid: Optional uuid for the procedure instance.
        """
        proc = self._create_procedure(device, procedure)
        entry = {
            'proc': proc,
            'device': device,
            'procedure': procedure,
            'requirements': {},
        }
        if not uuid:
            uuid = str(uuid4())
        self.procedures[uuid] = entry
        return uuid

    def updateProcedure(self, uuid, requirements):
        """
        Updates a procedure with new requirements.
        :param uuid: Uuid of the instantiated proecedure.
        :param requirements: Screen.virtualX
        """
        if uuid in self.procedures:
            self.procedures[uuid]['requirements'] = requirements

    def removeProcedure(self, uuid):
        """
        Deletes an instantiated procedure and all it's users.
        :param uuid: Uuid of the instantiated procedure.
        """
        for i, item in reversed(list(enumerate(self.proclist))):
            if item['uuid'] == uuid:
                self.proclist.pop(i)
        if uuid in self.procedures:
            del self.procedures[uuid]

    def do(self, device, procedure, requirements):
        """
        Does a procedure without instantiating it.
        :param device: Name of the device.
        :param procedure: Name of the procedure.
        :param requirements: Procedure requirements.
        """
        proc = self._create_procedure(device, procedure)
        reqs = self._resolve_requirements(requirements, device)
        proc.Do(reqs)

    def doProcedure(self, uuid, requirements):
        """
        Does a procedure from the instantiated procedures.
        """
        item = self.procedures[uuid]
        raw_reqs = item['requirements']
        raw_reqs.update(requirements)
        reqs = self._resolve_requirements(raw_reqs, item['device'])
        item['proc'].Do(reqs)

    def doProclistItem(self, index):
        """
        Does a procedure already in the procedure list.
        """
        item = self.proclist[index]
        self.doProcedure(uuid=item['uuid'], requirements=item['requirements'])

    def doProclist(self):
        """
        Does all the procedures in the procedure list
        """
        for i in range(len(self.proclist)):
            self.doProclistItem(i)

    def getProclist(self):
        """
        Returns the complete proclist
        """
        return [
            {
                'device': self.procedures[proc['uuid']]['device'],
                'procedure': self.procedures[proc['uuid']]['procedure'],
                'uuid': proc['uuid'],
                'requirements': proc['requirements'],
            }
            for proc in self.proclist
        ]

    def clearProclist(self):
        """
        Deletes all procedures in the proclist
        """
        del self.proclist[:]

    def exportProclist(self, fname):
        """
        Export the proclist and procedures to a JSON file.
        :param fname: Name of the JSON file.
        """
        jsonfile = open(fname, mode='w')
        data = {'procedures': self.getProcedures(), 'proclist': self.getProclist()}
        json.dump(data, jsonfile, indent=2, sort_keys=True)
        jsonfile.close()

    def importProclist(self, fname):
        """
        Import proclist and procedures from a JSON files.
        :param fname: Name of the JSON file.
        """
        with open(fname, 'r') as old_proclist:
            data = json.load(old_proclist)
        del self.proclist[:]
        self.procedures.clear()
        for item in data['procedures']:
            uuid = self.createProcedure(item['device'], item['procedure'], item['uuid'])
            self.updateProcedure(uuid, item['requirements'])
        for item in data['proclist']:
            self.insertProclistItem(-1, item['uuid'], item['requirements'])

    def insertProclistItem(self, index, uuid, requirements):
        """
        Inserts a new procedure into the proclist
        :param index: Append if -1 else insert into list.
        :param uuid: Uuid of the instantiated procedure.
        :param requirements: Procedure requirements.
        """
        if uuid not in self.procedures:
            raise KeyError(f"Procedure instance {uuid} not found")
        entry = {'uuid': uuid, 'requirements': requirements}
        if index == -1:
            self.proclist.append(entry)
        elif index < len(self.proclist):
            self.proclist.insert(index, entry)
        else:
            raise IndexError("Index must be -1 or in range")

    def updateProclistItem(self, index, requirements):
        """
        Updates an existing procedure in the proclist.
        :param index: Index of the procedure in the list.
        :param requirements: New procedure requirements.
        """
        self.proclist[index]['requirements'] = requirements

    def removeProclistItem(self, index):
        """
        Deletes a single procedure from the proclist.
        :param index: Index of the procedure in the list.
        """
        del self.proclist[index]

    def swapProclistItems(self, index1, index2):
        """
        Swaps the position of two procedures in the list.
        :param index1: Index of the first procedure.
        :param index2: Index of the second procedure.
        """
        self.proclist[index1], self.proclist[index2] = (
            self.proclist[index2],
            self.proclist[index1],
        )
