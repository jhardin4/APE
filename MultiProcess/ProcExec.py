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
        self.executor = Core.Executor()
        self.executor.node = self.node
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

    def do(self, device, procedure, requirements):
        """
        Does a procedure immediately and does not add it to the procedure list
        """
        proc = self._create_procedure(device, procedure, bool(requirements))
        reqs = self._resolve_requirements(requirements)
        proc(reqs)

    def _resolve_value(self, value):
        # reference syntax
        if value.startswith('@'):
            real_value = self.apparatus.getValue(value[1:].split('/'))
            return real_value

        # procedure syntax
        elif value.startswith('!'):
            try:
                real_value = getattr(Project_Procedures, value[1:])(
                    self.apparatus, self.executor
                )
            except AttributeError:
                real_value = None
            return real_value

        else:
            return value

    def _resolve_requirements(self, reqs):
        filled = reqs.copy()
        for name, value in filled.items():
            if isinstance(value, str):
                real_value = self._resolve_value(value)
                filled[name] = real_value
        return filled

    def doProc(self, index):
        """
        Does a procedure already added to the procedure list
        """
        proc = self.proclist[index]
        reqs = self._resolve_requirements(proc['requirements'])
        proc['proc'](reqs)

    def doProclist(self):
        """
        Does all the procedures in the procedure list
        """
        for i in range(len(self.proclist)):
            self.doProc(i)

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
        :return:
        """
        del self.proclist[:]

    def exportProclist(self, fname):
        jsonfile = open(fname, mode='w')
        json.dump(self.getProclist(), jsonfile, indent=2, sort_keys=True)
        jsonfile.close()

    def importProclist(self, fname):
        with open(fname, 'r') as old_proclist:
            data = json.load(old_proclist)
        self.proclist = []
        for item in data:
            self.insertProc(-1, item['device'], item['procedure'], item['requirements'])

    def insertProc(self, index, device, procedure, requirements):
        """
        Inserts a new procedure into the proclist
        :param index: Append if -1 else insert into list.
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
        if index == -1:
            self.proclist.append(entry)
        elif index < len(self.proclist):
            self.proclist.insert(index, entry)
        else:
            raise IndexError()

    def updateProc(self, index, requirements):
        """
        Updates an existing procedure in the proclist.
        :param index: Index of the procedure in the list.
        :param requirements: New procedure requirements.
        """
        self.proclist[index]['requirements'] = requirements

    def removeProc(self, index):
        """
        Deletes a single procedure from the proclist.
        :param index: Index of the procedure in the list.
        """
        del self.proclist[index]

    def swapProcs(self, index1, index2):
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
