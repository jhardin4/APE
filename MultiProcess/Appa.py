import Core
from MultiProcess import APE_Interfaces
from MultiProcess.zmqNode import zmqNode
from importlib import import_module


class Appa:
    def __init__(self, A2L_address, A2PE_address, A2G_address):
        # Create the node and set its target to Appa
        self.node = zmqNode('appa')
        self.node.target = self
        self.node.logging = True
        # Create a black Apparatus
        self.apparatus = Core.Apparatus()
        # Create an interface for the executor and assign it to the apparatus
        self.executor = APE_Interfaces.ExecutorInterface(self.node)
        self.executor.localDefault = False
        self.apparatus.executor = self.executor
        # Connect to the gui, launcher, and procexec process
        self.connect2L(A2L_address)
        self.connect2PE(A2PE_address)
        self.connect2G(A2G_address)
        self.node.start_listening()

    # connects to PE and G as server, L as client
    def connect2L(self, A2L_address):
        self.node.connect('launcher', A2L_address)

    def connect2PE(self, A2PE_address):
        self.node.connect('procexec', A2PE_address, server=True)

    def connect2G(self, A2G_address):
        self.node.connect('gui', A2G_address, server=True)

    def createApparatus(self, template, args, kwargs):
        self.apparatus = Core.Apparatus()
        if template == 'file':
            self.apparatus = Core.Apparatus()
        else:
            templateFunc = import_module(template)
            templateFunc(*args, **kwargs)


if __name__ == '__main__':
    pass
