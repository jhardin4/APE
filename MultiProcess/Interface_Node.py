from zmqNode import zmqNode
import Devices
import APE_Interfaces

# This used for interfacing with an APE process
# It is built on the zmqNode
# Most Methods are just commonly used messages


class Interface_Node():
    def __init__(self, I2A_address, I2PE_address):
        self.node = zmqNode('User')
        self.node.target = self
        self.node.logging = True
        self.apparatus = APE_Interfaces.ApparatusInterface(self.node)
        self.apparatus.defaultBlocking = False
        self.executor = APE_Interfaces.ExecutorInterface(self.node)
        self.User = Devices.User_Consol('User')
        self.connect2A(I2A_address)
        self.connect2PE(I2PE_address)
        self.node.start_listening()

    def connect2A(self, I2A_address):
        self.node.connect('appa', I2A_address)

    def connect2PE(self, I2PE_address):
        self.node.connect('procexec', I2PE_address)

    def test_print(self, message):
        print(str(message))

    def sendCloseAll(self):
        message = {'subject': 'close'}
        for connection in self.node.connections:
            self.node.send(connection, message)

    def DoProclist(self):
        message = {'subject': 'target.DoProclist'}
        self.node.send('procexec', message)

    def getInput(message, option):
        pass


if __name__ == '__main__':
    pass
