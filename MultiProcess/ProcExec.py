import json

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
        self.procedures = {}
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

    def _create_procedure(self, device, procedure, requirements):
        if device == '':
            raw_proc = getattr(Procedures, procedure, None)
            if raw_proc is None:
                raw_proc = getattr(Project_Procedures, procedure)
            raw_proc = raw_proc(self.apparatus, self.executor)
            if not requirements:

                def proc(_):
                    raw_proc.Do()

            else:

                def proc(reqs):
                    raw_proc.Do(reqs)

        else:

            def proc(reqs):
                self.apparatus.DoEproc(device, procedure, reqs)

        return proc

    def _resolve_value(self, value, eproc):
        # reference syntax
        if value.startswith('@'):
            real_value = self.apparatus.getValue(value[1:].split('/'))
            return real_value

        # procedure syntax
        elif value.startswith('!') and not eproc:
            try:
                real_value = getattr(Project_Procedures, value[1:])(
                    self.apparatus, self.executor
                )
            except AttributeError:
                real_value = None
            return real_value

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
            {
                'device': proc['device'],
                'procedure': proc['procedure'],
                'requirements': proc['requirements'],
            }
            for proc in self.procedures.values()
        ]

    def clearProcedures(self):
        """
        Deletes all instantiated procedures.
        """
        self.procedures.clear()
        self.clearProclist()

    def createProcedure(self, device, procedure, requirements):
        """
        Instantiates a new procedure.
        :param device: Name of the device.
        :param procedure: Name of the procedure.
        :param requirements: Procedure requirements.
        """
        proc = self._create_procedure(device, procedure, bool(requirements))
        entry = {
            'proc': proc,
            'device': device,
            'procedure': procedure,
            'requirements': requirements,
        }
        self.procedures[f'{device}/{procedure}'] = entry

    def removeProcedure(self, device, procedure):
        """
        Deletes an instantiated procedure and all it's users.
        :param device: Name of the device.
        :param procedure: Name of the procedure.
        """
        for item in self.proclist:
            if item['device'] == device and item['procedure'] == procedure:
                self.proclist.remove(item)
        ref = f'{device}/{procedure}'
        if ref in self.procedures:
            del self.procedures[ref]

    def doProcedure(self, device, procedure):
        """
        Does a procedure from the instantiated procedures.
        """
        proc = self.procedures[f'{device}/{procedure}']
        reqs = self._resolve_requirements(proc['requirements'], eproc=bool(device))
        proc['proc'](reqs)

    def doProclistItem(self, index):
        """
        Does a procedure already in the procedure list.
        """
        item = self.proclist[index]
        proc = self.procedures[f'{item["device"]}/{item["procedure"]}']
        reqs = self._resolve_requirements(
            item['requirements'], eproc=bool(item['device'])
        )
        proc['proc'](reqs)

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
                'device': proc['device'],
                'procedure': proc['procedure'],
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
            self.createProcedure(
                item['device'], item['procedure'], item['requirements']
            )
        for item in data['proclist']:
            self.insertProclistItem(
                -1, item['device'], item['procedure'], item['requirements']
            )

    def insertProclistItem(self, index, device, procedure, requirements):
        """
        Inserts a new procedure into the proclist
        :param index: Append if -1 else insert into list.
        :param device: Name of the device.
        :param procedure: Name of the procedure.
        :param requirements: Procedure requirements.
        """
        if f'{device}/{procedure}' not in self.procedures:
            raise KeyError("Procedure not found")
        entry = {'device': device, 'procedure': procedure, 'requirements': requirements}
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


if __name__ == '__main__':
    pass
