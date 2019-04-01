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

    def execute(self, eproclist):
        # This could take a list of multiple lists of eprocs but typically it 
        # is only a list of a single eproc
        for line in eproclist:
            for eproc in line:
                # This loop creates the blocking action for non-blocking
                # message passing.
                while not self.ready4next:
                    # it is important for the listen to be in the loop to
                    # ensure that there is a way out
                    self.node.listen(self.prevDevice)
                self.Send(eproc)

    def loadDevice(self, devName, devAddress, devAddressType):
        self.devicelist[devName] = {}
        self.devicelist[devName]['Address'] = devAddress
        self.devicelist[devName]['AddressType'] = devAddressType

    def createDevice(self, devName, devType, devAddressType):
        self.devicelist[devName] = {}
        self.devicelist[devName]['Address'] = getattr(Devices, devType)(devName)
        self.devicelist[devName]['AddressType'] = devAddressType

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
            self.prevDevice = eproc['devices']
            message = {}
            message['subject'] = 'target.' + eproc['devices'] + '.' + eproc['procedure']
            message['kwargs'] = eproc['details']
            message['ereply'] = {}
            message['ereply']['subject'] = 'target.executor.logResponse'
            message['ereply']['args'] = ['e_proc']
            self.node.send(eproc['devices'], message)

    def logResponse(self, message):
        self.ready4next = True
        if self.logging:
            loghandle = open('Logs/' + self.logaddress, mode='a')
            loghandle.write(self.log)
            loghandle.close()
            self.log = ''     
            
