import Core
from zmqNode import zmqNode
import APE_Interfaces


class ProcExec():
    def __init__(self, PE2I_address, PE2A_address):
        self.node = zmqNode('procexec')
        self.node.target = self
        self.node.logging = True
        self.executor = Core.Executor()
        self.executor.node = self.node
        self.proclist = []
        self.apparatus = APE_Interfaces.ApparatusInterface(self.node)
        self.connect2I(PE2I_address)
        self.connect2A(PE2A_address)
        self.node.start_listening()

    def connect2I(self, PE2I_address):
        self.node.connect('User', PE2I_address, server=True)

    def connect2A(self, PE2A_address):
        self.node.connect('appa', PE2A_address)

    # Does a procedure immediately and does not add it to the procedure list
    def Do(self, procedure, requirements):
        if requirements == {}:
            procedure.Do()
        else:
            procedure.Do(requirements)

    def DoProclist(self):
        for line in self.proclist:
            self.Do(line['procedure'], line['requirements'])


if __name__ == '__main__':
    pass
