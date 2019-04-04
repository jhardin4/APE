import Core
import APE_Interfaces
from zmqNode import zmqNode
import threading

class Appa():
    def __init__(self, A2I_address, A2PE_address):
        # Create the node and set its target to Appa
        self.node = zmqNode('appa')
        self.node.target = self
        self.node.logging = True
        # Create an Apparatus
        self.apparatus = Core.Apparatus()
        # Create an interface to for the executor and assign it to the apparatus
        self.executor = APE_Interfaces.ExecutorInterface(self.node)
        self.executor.localDefault = False
        self.apparatus.executor = self.executor
        # Connect to the user interface and procexec process
        self.connect2I(A2I_address)
        self.connect2PE(A2PE_address)
        self.node.start_listening()

    def connect2I(self, A2I_address):
        self.node.connect('User', A2I_address, server=True)

    def connect2PE(self, A2PE_address):
        self.node.connect('procexec', A2PE_address, server=True)


if __name__ == '__main__':
    from multiprocessing import Process
    test = 1
    address = "tcp://127.0.0.1:5557"
    if test == 1:
        test = Process(target=StartAPE, args=(address,))
        test.start()
        comNode = zmqNode()
        comNode.logfile = 'comNode.txt'
        comNode.connect('server', address)
        #return_message = {'command': 'setValue', 'information': {'infoAddress': ['information', 'calibrationfile'], 'value': 'bleh'}}
        #message = {'type': 'target_command', 'command': 'CMD_Apparatus', 'data': {'message': return_message}}
        
        # Testing Node
        return_message = {'subject': 'node', 'action': 'zprint', 'kwargs': {'message': 'testing'}}
        message = {'ereply': return_message}
        comNode.send('server', message)
        threading.Timer(1, comNode.listen_all).start()
        threading.Timer(1.1, comNode.listen_all).start()
        
        # Changing Value in apparatus
        kwargs1 = {'command': 'setValue', 'information': {'infoAddress': ['information', 'calibrationfile'], 'value': 'bleh'}}
        message1 = {'subject': 'target', 'action': 'CMD_Apparatus', 'kwargs': kwargs1}
        threading.Timer(1.2, comNode.send, args=['server', message1]).start()
        
        # Retrieving Value
        kwargs2 = {'command': 'getValue', 'information': {'infoAddress': ['information', 'calibrationfile']}}
        return_message = {'subject': 'node', 'action': 'zprint', 'kwargs': {'message': 'e_reply'}}
        message2 = {'subject': 'target', 'action': 'CMD_Apparatus', 'kwargs': kwargs2, 'ereply':return_message}
        threading.Timer(1.3, comNode.send, args=['server', message2]).start()
        
        threading.Timer(1.4, comNode.listen_all).start()
        
        # Close things out
        threading.Timer(3.5, print, args=[str(test.is_alive())]).start()
        close_message = {'subject': 'node', 'action': 'close'}
        threading.Timer(4, comNode.send, args=['server', close_message]).start()
        threading.Timer(4.5, print, args=[str(test.is_alive())]).start()
        threading.Timer(5, test.join).start()
        threading.Timer(6, print, args=[str(test.is_alive())]).start()

    elif test == 2:
        test = StartAPE('')
        print(test.CMD_Apparatus(command='getValue', information={'infoAddress': ['information', 'calibrationfile']}))
