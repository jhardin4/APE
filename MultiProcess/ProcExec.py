import Core
from MultiProcess.zmqNode import zmqNode
from MultiProcess import APE_Interfaces


class ProcExec():
    def __init__(self, PE2L_address, PE2A_address, PE2G_address):
        # Create the node and set its target to ProcExec
        self.node = zmqNode('procexec')
        self.node.target = self
        self.node.logging = True
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
        #need a def creatproc(name, filename/path)
    # connects to G as server, L and A as client
    def connect2L(self, PE2L_address):
        self.node.connect('launcher', PE2L_address)

    def connect2A(self, PE2A_address):
        self.node.connect('appa', PE2A_address)
    
    def connect2G(self, PE2G_address):
        self.node.connect('gui', PE2G_address, server=True)

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
