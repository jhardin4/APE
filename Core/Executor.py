import time
import sys
import Devices


class Executor():
    def __init__(self):
        self.devicelist = {}
        self.log = ''
        self.logaddress = str(int(round(time.time(), 0))) + 'log.txt'
        self.logging = True
        self.debug = False
        self.ready4next = True
        self.node = ''
        self.prevDevice = ''
        self.loopBlocks = {}

    def execute(self, eproclist):
        # This could take a list of multiple lists of eprocs but typically it 
        # is only a list of a single eproc
        for line in eproclist:
            for eproc in line:
                # This loop creates the blocking action for non-blocking
                # message passing.
                while not self.ready4next:
                    pass
                    # it is important for the listen to be in the loop to
                    # ensure that there is a way out
                self.Send(eproc)

    def loadDevice(self, devName, devAddress, devAddressType):
        self.devicelist[devName] = {}
        self.devicelist[devName]['Address'] = devAddress
        self.devicelist[devName]['AddressType'] = devAddressType
        self.devicelist[devName]['Address'].executor = self

    def createDevice(self, devName, devType, exec_address, rel_address):
        # Handle local creation of a device
        if self.node.name == rel_address:
            self.devicelist[devName] = {}
            self.devicelist[devName]['Address'] = getattr(Devices, devType)(devName)
            self.devicelist[devName]['AddressType'] = 'pointer'
            self.devicelist[devName]['Address'].executor = self
        else:
            self.devicelist[devName] = {}
            self.devicelist[devName]['Address'] = rel_address
            self.devicelist[devName]['AddressType'] = 'zmqNode'
            ereply = {}
            ereply['subject'] = 'target.executor.recv_value'
            ereply['args'] = ['devMade', 'e_reply']
    
            # Build primary message
            args = [devName, devType, exec_address, rel_address]
            message = {'subject': 'target.executor.createDevice',
                       'args':args,
                       'ereply': ereply}
            self.loopBlocks['devMade'] = False
            self.node.send(rel_address, message)
            cur_connection  = self.node.cur_connection
            while not self.loopBlocks['devMade']:
                self.node.listen(rel_address)
            self.node.cur_connection  = cur_connection

    def Send(self, eproc):
        if self.devicelist[eproc['devices']]['AddressType'] == 'pointer':
            if not self.debug:
                try:
                    self.log += "Time: " + str(round(time.time(), 3)) + '\n'
                    if eproc['details'] == {}:
                        self.log += getattr(self.devicelist[eproc['devices']]['Address'],
                                            eproc['procedure'])()
                    else:
                        self.log += getattr(self.devicelist[eproc['devices']]['Address'],
                                            eproc['procedure'])(**eproc['details'])

                    self.log += '\n'

                    self.logResponse(self.log)

                except Exception:
                    print('The following line failed to send:\n' + str(eproc))
                    print("Oops!", sys.exc_info()[0], "occured.")
                    raise Exception('EXECUTOR SEND FAILURE')

            else:
                self.log += "Time: " + str(round(time.time(), 3)) + '\n'
                if eproc['details'] == {}:
                    self.log += getattr(self.devicelist[eproc['devices']]['Address'],
                                        eproc['procedure'])()
                else:
                    self.log += getattr(self.devicelist[eproc['devices']]['Address'],
                                        eproc['procedure'])(**eproc['details'])

                self.log += '\n'
                
                self.logResponse(self.log)


        elif self.devicelist[eproc['devices']]['AddressType'] == 'zmqNode':
            self.ready4next = False
            self.prevDevice = self.devicelist[eproc['devices']]['Address']
            message = {}
            message['subject'] = 'target.executor.devicelist["' + eproc['devices'] + '"]["Address"].' + eproc['procedure']
            message['kwargs'] = eproc['details']
            message['ereply'] = {}
            message['ereply']['subject'] = 'target.executor.logResponse'
            message['ereply']['args'] = ['e_reply']
            self.node.send(self.devicelist[eproc['devices']]['Address'], message)
            while not self.ready4next:
                    self.node.listen(self.prevDevice)

    def logResponse(self, message):
        self.ready4next = True
        if self.logging:
            loghandle = open('Logs/' + self.logaddress, mode='a')
            loghandle.write(message)
            loghandle.close()
            self.log = ''

    def recv_value(self, target, value):
        self.loopBlocks[target] = True
        self.returnedValue = value

    def getDependencies(self, device):
        return self.devicelist[device]["Address"].getDependencies()
