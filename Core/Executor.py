import time
import sys
import Devices
from MultiProcess.APE_Interfaces import ApeInterface


class Executor(ApeInterface):
    def __init__(self, node=None):
        super(Executor, self).__init__(node, recv_subject='target.executor.recv_value')
        self.devicelist = {}
        self.log = ''
        self.logaddress = str(int(round(time.time(), 0))) + 'log.txt'
        self.logging = True
        self.debug = False
        self.ready4next = True
        self.node = node
        self.prevDevice = ''

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
            try:
                device = getattr(Devices, devType)(devName)
            except AttributeError:
                return False
            self.devicelist[devName] = {}
            self.devicelist[devName]['Address'] = device
            self.devicelist[devName]['AddressType'] = 'pointer'
            self.devicelist[devName]['Address'].executor = self
            return True
        else:
            self.devicelist[devName] = {}
            self.devicelist[devName]['Address'] = rel_address
            self.devicelist[devName]['AddressType'] = 'zmqNode'
            return self._send_message(
                subject='target.executor.createDevice',
                args=[devName, devType, rel_address, rel_address],
                target=rel_address,
            )

    def Send(self, eproc):
        if self.devicelist[eproc['devices']]['AddressType'] == 'pointer':
            if not self.debug:
                try:
                    self.log += "Time: " + str(round(time.time(), 3)) + '\n'
                    if eproc['details'] == {}:
                        self.log += getattr(
                            self.devicelist[eproc['devices']]['Address'],
                            eproc['procedure'],
                        )()
                    else:
                        self.log += getattr(
                            self.devicelist[eproc['devices']]['Address'],
                            eproc['procedure'],
                        )(**eproc['details'])

                    self.log += '\n'

                    self.logResponse(self.log)

                except Exception:
                    print('The following line failed to send:\n' + str(eproc))
                    print("Oops!", sys.exc_info()[0], "occured.")
                    raise Exception('EXECUTOR SEND FAILURE')

            else:
                self.log += "Time: " + str(round(time.time(), 3)) + '\n'
                if eproc['details'] == {}:
                    self.log += getattr(
                        self.devicelist[eproc['devices']]['Address'], eproc['procedure']
                    )()
                else:
                    self.log += getattr(
                        self.devicelist[eproc['devices']]['Address'], eproc['procedure']
                    )(**eproc['details'])

                self.log += '\n'

                self.logResponse(self.log)

        elif self.devicelist[eproc['devices']]['AddressType'] == 'zmqNode':
            self.ready4next = False
            self.prevDevice = self.devicelist[eproc['devices']]['Address']
            message = {}
            message['subject'] = (
                'target.executor.devicelist["'
                + eproc['devices']
                + '"]["Address"].'
                + eproc['procedure']
            )
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
            loghandle.write(str(message))
            loghandle.close()
            self.log = ''

    def getDependencies(self, device, address):
        if address == self.node.name:
            return self.devicelist[device]["Address"].getDependencies()
        else:
            return self._send_message(
                subject='target.executor.getDependencies',
                args=[device, address],
                target=address,
            )

    def getDevices(self, address):
        if address == self.node.name:
            return [
                name
                for name, device in self.devicelist.items()
                if device["AddressType"] != "zmqNode"
            ]
        else:
            return self._send_message(
                subject='target.executor.getDevices', args=[address], target=address
            )

    def getEprocs(self, device, address):
        if address == self.node.name:
            return list(self.devicelist[device]['Address'].requirements)
        else:
            return self._send_message(
                subject='target.executor.getEprocs',
                args=[device, address],
                target=address,
            )

    def getRequirements(self, device, eproc, address):
        if address == self.node.name:
            return list(self.devicelist[device]['Address'].requirements[eproc])
        else:
            return self._send_message(
                subject='target.getRequirements',
                args=[device, eproc, address],
                target=address,
            )
