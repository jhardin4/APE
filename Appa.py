import Core
from zmqNode import zmqNode
import threading

class Appa():
    def __init__(self):
        self.apparatus = Core.Apparatus()
        self.com_node = ''
        
    def connect_node(self, address=''):
        if address == '':
            address = self.address
        self.com_node.connect('server', address, server=True)
        self.address = address
        self.com_node.start_listening()
    
    # Does a procedure immediately and does not add it to the procedure list
    def Do(self, procedure, requirements):
        if requirements == {}:
            procedure.Do()
        else:
            procedure.Do(requirements)
    
    def DoProclist(self):
        for line in self.proclist:
            self.Do(line['procedure'], line['requirements'])


def StartAPE(address):
    MyAPE = APE()
    import FlexPrinterApparatus
    materials = [{'AgPMMA': 'ZZ1'}]
    # These are other tools that can be added in. Comment out the ones not used.
    tools = []
    # tools.append({'name': 'TProbe', 'axis': 'ZZ2', 'type': 'Keyence_GT2_A3200'})
    # tools.append({'name': 'camera', 'axis': 'ZZ4', 'type': 'IDS_ueye'})
    FlexPrinterApparatus.Build_FlexPrinter(materials, tools, MyAPE.apparatus)

    if address != '':
        MyAPE.com_node = zmqNode('server')
        MyAPE.com_node.target = MyAPE
        MyAPE.connect_node(address)
    return MyAPE


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
