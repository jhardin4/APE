import APE
from MultiProcess.zmqNode import zmqNode
from multiprocessing import Process


class APE_GUI_Node:
    def __init__(self):
        self.node = zmqNode()
        self.node.target = self

    def startNode(self, address):
        self.node.logfile = 'GUINode.txt'
        self.node.connect('APE', address)
        self.node.start_listening()

    def setValue(self, app_address, value):
        kwargs = {
            'command': 'setValue',
            'information': {'infoAddress': app_address, 'value': value},
        }
        message = {'subject': 'target', 'action': 'CMD_Apparatus', 'kwargs': kwargs}
        self.node.send('APE', message)

    def getValue(self, app_address, local_method, local_args='', local_kwargs=''):
        # Build expected reply
        ereply = {}
        ereply['subject'] = 'target'
        ereply['action'] = local_method  # This is a string not a method!
        if local_args != '':
            ereply['args'] = local_args
        if local_kwargs != '':
            ereply['kwargs'] = local_kwargs

        # Build primary message
        kwargs = {'command': 'getValue', 'information': {'infoAddress': app_address}}
        message = {
            'subject': 'target',
            'action': 'CMD_Apparatus',
            'kwargs': kwargs,
            'ereply': ereply,
        }
        self.node.send('APE', message)

    def test_print(self, message):
        print(str(message))


if __name__ == '__main__':
    address = "tcp://127.0.0.1:5562"
    proc_APE = Process(target=APE.StartAPE, args=(address,))
    proc_APE.start()
    banana = APE_GUI_Node()
    banana.startNode(address)
    banana.getValue(
        ['information', 'calibrationfile'], 'test_print', local_args=['e_reply']
    )
