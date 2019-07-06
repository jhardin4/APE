# -*- coding: utf-8 -*-
from MultiProcess import APE_Interfaces
from MultiProcess.zmqNode import zmqNode


class GUI_Node:
    def __init__(self, G2L_address, G2A_address, G2PE_address):
        # Create the node
        self.node = zmqNode('gui')
        self.node.logging = True
        # self.User = Devices.User_GUI('User')
        # Create an interface for the executor and apparatus
        # assigns them to the gui
        self.apparatus = APE_Interfaces.ApparatusInterface(self.node)
        self.executor = APE_Interfaces.ExecutorInterface(self.node)
        # connect to launcher, apparatus, and procexec
        self.connect2A(G2A_address)
        self.connect2PE(G2PE_address)
        self.connect2L(G2L_address)
        self.GUI = None
        # sets the target to be the GUI
        self.node.target = self
        # sets the interface apparatus to the apparatus in the GUI

        self.node.start_listening()

    # connects to all of the other nodes as client
    # server MUST be false for all of these (preset)
    def connect2A(self, G2A_address):
        self.node.connect('appa', G2A_address)

    def connect2PE(self, G2PE_address):
        self.node.connect('procexec', G2PE_address)

    def connect2L(self, G2L_address):
        self.node.connect('launcher', G2L_address)
