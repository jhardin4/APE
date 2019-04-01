from zmqNode import zmqNode
import threading
import APE
from multiprocessing import Process
import time
import Devices

# This used for interfacing with and APE process
# It is built on the zmqNode
# Most Methods are just commonly used messages

class Interface_Node():
    def __init__(self):
        self.node = zmqNode('Interface')
        self.node.target = self
        self.User = Devices.User_Consol('User')

    def startNode(self):
        self.node.start_listening()

    def Connect_All(self):
        message = {'subject': 'target.Connect_All'}
        self.node.send('appa', message)
   
    def setValue(self, app_address, value):
        kwargs = {'infoAddress': app_address, 'value': value}
        message = {'subject': 'target.setValue', 'kwargs': kwargs}
        self.node.send('appa', message)
    
    
    def getValue(self, app_address, local_method, local_args='', local_kwargs=''):
        #Build expected reply
        ereply = {}
        ereply['subject'] = 'target.' + local_method
        if local_args != '':
            ereply['args'] = local_args
        if local_kwargs != '':
            ereply['kwargs'] = local_kwargs

        # Build primary message
        kwargs = {'infoAddress': app_address}
        message = {'subject': 'target.getValue', 'kwargs': kwargs, 'ereply': ereply}
        self.node.send('appa', message)

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
    address = "tcp://127.0.0.1:5576"
    proc_APE = Process(target=APE.StartAPE, args=(address,))
    proc_APE.start()
    banana = Interface_Node()
    banana.startNode(address)
    print(time.time())
    banana.getValue(['information', 'calibrationfile'], 'test_print', local_args=['e_reply'])
    print(time.time())
    threading.Timer(2, banana.sendClose).start()
    threading.Timer(2.1, banana.node.close).start()
    threading.Timer(2.2, proc_APE.join).start()
    
    