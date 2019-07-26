# These are interfaces that simplify communication between
import Devices


class ApeInterface:
    def __init__(self, node, recv_subject, target=''):
        self.loopBlocks = {}
        self.returnedValue = None
        self.default_blocking = True
        self.node = node
        self.recv_subject = recv_subject
        self.default_target = target

    def _send_message(
        self, subject, kwargs=None, args=None, reply=None, target=None, json_args=None
    ):
        if json_args is None:
            json_args = {}
        if target is None:
            target = self.default_target
        if reply is None:
            reply = self.default_blocking
        message = {'subject': subject}
        if reply:
            # Build expected reply
            message['ereply'] = {
                'subject': self.recv_subject,
                'args': [subject, 'e_reply'],
            }
        if kwargs:
            message['kwargs'] = kwargs
        if args:
            message['args'] = args

        if reply:
            self.loopBlocks[subject] = False
        self.node.send(target, message, **json_args)
        if reply:
            while not self.loopBlocks[subject]:
                self.node.listen(target)
            return self.returnedValue

    def recv_value(self, target, value):
        self.loopBlocks[target] = True
        self.returnedValue = value


class ApparatusInterface(ApeInterface):
    def __init__(self, node):
        super(ApparatusInterface, self).__init__(
            node, recv_subject='target.apparatus.recv_value', target='appa'
        )
        self.apparatus_address = ''

    def Connect_All(self, simulation=False):
        self._send_message(
            subject='target.apparatus.Connect_All', kwargs={'simulation': simulation}
        )

    def Disconnect_All(self):
        self._send_message(subject='target.apparatus.Disconnect_All')

    def setValue(self, app_address, value):
        self._send_message(
            subject='target.apparatus.setValue',
            kwargs={'infoAddress': app_address, 'value': value},
        )

    def getValue(self, app_address):
        return self._send_message(
            subject='target.apparatus.getValue', kwargs={'infoAddress': app_address}
        )

    def checkAddress(self, app_address):
        return self._send_message(
            subject='target.apparatus.checkAddress', kwargs={'infoAddress': app_address}
        )

    def createAppEntry(self, app_address):
        return self._send_message(
            subject='target.apparatus.createAppEntry', args=[app_address]
        )

    def removeAppEntry(self, app_address):
        return self._send_message(
            subject='target.apparatus.removeAppEntry', args=[app_address]
        )

    def LogProc(self, name, requirements):
        self._send_message(
            'target.apparatus.LogProc',
            args=[name, requirements],
            reply=False,
            json_args={'default': lambda o: '<not serializable>'},
        )

    def findDevice(self, reqs):
        return self._send_message(subject='target.apparatus.findDevice', args=[reqs])

    def serialClone(self, address=None):
        return self._send_message(
            subject='target.apparatus.serialClone', kwargs={'address': address}
        )

    def applyTemplate(self, tName, args=None, kwargs=None):
        if kwargs is None:
            kwargs = {}
        if args is None:
            args = []
        self._send_message(
            subject='target.apparatus.applyTemplate',
            args=[tName],
            kwargs={'args': args, 'kwargs': kwargs},
        )

    def logApparatus(self, fname):
        self._send_message(
            subject='target.apparatus.logApparatus', args=[fname], reply=False
        )

    def importApparatus(self, fname):
        self._send_message(subject='target.apparatus.importApparatus', args=[fname])

    def DoEproc(self, device, method, details):
        return self._send_message(
            subject='target.apparatus.DoEproc', args=[device, method, details]
        )


class ExecutorInterface(ApeInterface):
    def __init__(self, node):
        super(ExecutorInterface, self).__init__(
            node, recv_subject='target.executor.recv_value', target='procexec'
        )
        self.devicelist = {}
        self.localDefault = True

    def execute(self, eproclist):
        self._send_message(subject='target.executor.execute', args=[eproclist])

    def createDevice(self, devName, devType, exec_address, rel_address):
        # Handle local creation of a device
        if self.node.name == rel_address == exec_address:
            self.devicelist[devName] = {}
            self.devicelist[devName]['Address'] = getattr(Devices, devType)(devName)
            self.devicelist[devName]['AddressType'] = 'pointer'
            self.devicelist[devName]['Address'].executor = self
            return True
        else:
            return self._send_message(
                subject='target.executor.createDevice',
                args=[devName, devType, exec_address, rel_address],
                target=exec_address,
            )

    def getDescriptors(self, device, address):
        if address == self.node.name:
            return self.devicelist[device]["Address"].getDescriptors()

        subject = f'target.executor.devicelist["{device}"]["Address"].getDescriptors'
        return self._send_message(subject=subject, target=address)

    def setSimulation(self, device, value, address):
        if address == self.node.name:
            self.devicelist[device]["Address"].setSimulation(value)
            return

        subject = f'target.executor.devicelist["{device}"]["Address"].setSimulation'
        self._send_message(subject=subject, args=[value], target=address)

        # def getRequirements(self, device, eproc, address):
        # Build expected reply
        '''
        ereply = {}
        ereply['subject'] = 'target.executor.recv_value'
        ereply['args'] = ['gotRequirements', 'e_reply']

        # Build primary message
        args = [eproc]
        message = {'subject': 'target.executor.devicelist["' + device + '"]["Address"].getRequirements', 'args':args, 'ereply': ereply}
        self.loopBlocks['gotRequirements'] = False
        self.node.send(address, message)
        while not self.loopBlocks['gotRequirements']:
            self.node.listen(address)
        return self.returnedValue
        '''

    def getDependence(self, device, address):
        if address == self.node.name:
            self.devicelist[device]["Address"].getDependence()

        subject = f'target.executor.devicelist["{device}"]["Address"].getDependence'
        return self._send_message(subject=subject, target=address)

    def getDependencies(self, device, address):
        if address == self.node.name:
            return self.devicelist[device]["Address"].getDependencies()

        subject = f'target.executor.devicelist["{device}"]["Address"].getDependencies'
        return self._send_message(subject=subject, target=address)

    def getRequirements(self, device, eproc, address):
        if address == self.node.name:
            return list(self.devicelist[device]['Address'].requirements[eproc])

        return self._send_message(
            subject='target.executor.getRequirements',
            args=[device, eproc, address],
            target=address,
        )

    def getDevices(self, address):
        if address == self.node.name:
            return list(self.devicelist)

        return self._send_message(
            subject='target.executor.getDevices', args=[address], target=address
        )

    def getEprocs(self, device, address):
        if address == self.node.name:
            return list(self.devicelist[device]['Address'].requirements)

        return self._send_message(
            subject='target.executor.getEprocs', args=[device, address], target=address
        )

    def getProcedures(self):
        return self._send_message(subject='target.getProcedures')

    def clearProcedures(self):
        self._send_message(subject='target.clearProcedures')

    def reloadProcedures(self):
        self._send_message(subject='target.reloadProcedures')

    def createProcedure(self, device, procedure, requirements):
        self._send_message(
            subject='target.createProcedure', args=[device, procedure, requirements]
        )

    def removeProcedure(self, device, procedure):
        self._send_message(subject='target.removeProcedure', args=[device, procedure])

    def do(self, device, procedure, requirements):
        self._send_message(subject='target.do', args=[device, procedure, requirements])

    def doProcedure(self, device, procedure):
        self._send_message(subject='target.doProcedure', args=[device, procedure])

    def doProclistItem(self, index):
        self._send_message(subject='target.doProclistItem', args=[index])

    def doProclist(self):
        self._send_message(subject='target.doProclist')

    def getProclist(self):
        return self._send_message(subject='target.getProclist')

    def clearProclist(self):
        self._send_message(subject='target.clearProclist')

    def exportProclist(self, fname):
        self._send_message(subject='target.exportProclist', args=[fname])

    def importProclist(self, fname):
        self._send_message(subject='target.importProclist', args=[fname])

    def insertProclistItem(self, index, device, procedure, requirements):
        self._send_message(
            subject='target.insertProclistItem',
            args=[index, device, procedure, requirements],
        )

    def updateProclistItem(self, index, requirements):
        self._send_message(
            subject='target.updateProclistItem', args=[index, requirements]
        )

    def removeProclistItem(self, index):
        self._send_message(subject='target.removeProclistItem', args=[index])

    def swapProclistItems(self, index1, index2):
        self._send_message(subject='target.swapProclistItems', args=[index1, index2])
