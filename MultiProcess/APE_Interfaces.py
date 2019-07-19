# These are interfaces that simplify communication between
import Devices


class ApparatusInterface:
    def __init__(self, node):
        self.loopBlocks = {}
        self.valueReceived = True
        self.returnedValue = 0
        self.node = node
        self.apparatus_address = ''
        self.defaultBlocking = True

    def Connect_All(self, simulation=False):
        kwargs = {'simulation': simulation}
        message = {'subject': 'target.apparatus.Connect_All', 'kwargs': kwargs}
        self.node.send('appa', message)

    def Disconnect_All(self):
        message = {'subject': 'target.apparatus.Disconnect_All'}
        self.node.send('appa', message)

    def setValue(self, app_address, value):
        kwargs = {'infoAddress': app_address, 'value': value}
        message = {'subject': 'target.apparatus.setValue', 'kwargs': kwargs}
        self.node.send('appa', message)

    def getValue(self, app_address):
        # Build expected reply
        ereply = {}
        ereply['subject'] = 'target.apparatus.recv_value'
        ereply['args'] = ['gotValue', 'e_reply']

        # Build primary message
        kwargs = {'infoAddress': app_address}
        message = {
            'subject': 'target.apparatus.getValue',
            'kwargs': kwargs,
            'ereply': ereply,
        }
        self.loopBlocks['gotValue'] = False
        self.node.send('appa', message)
        while not self.loopBlocks['gotValue']:
            self.node.listen('appa')
        return self.returnedValue

    def createAppEntry(self, app_address):
        # Build expected reply
        ereply = {}
        ereply['subject'] = 'target.apparatus.recv_value'
        ereply['args'] = ['madeEntry', 'e_reply']

        # Build primary message
        args = [app_address]
        message = {
            'subject': 'target.apparatus.createAppEntry',
            'args': args,
            'ereply': ereply,
        }
        self.loopBlocks['madeEntry'] = False
        self.node.send('appa', message)
        while not self.loopBlocks['madeEntry']:
            self.node.listen('appa')
        return self.returnedValue

    def removeAppEntry(self, app_address):
        # Build expected reply
        ereply = {}
        ereply['subject'] = 'target.apparatus.recv_value'
        ereply['args'] = ['removedEntry', 'e_reply']

        # Build primary message
        args = [app_address]
        message = {
            'subject': 'target.apparatus.removeAppEntry',
            'args': args,
            'ereply': ereply,
        }
        self.loopBlocks['removedEntry'] = False
        self.node.send('appa', message)
        while not self.loopBlocks['removedEntry']:
            self.node.listen('appa')
        return self.returnedValue

    def recv_value(self, target, value):
        self.loopBlocks[target] = True
        self.returnedValue = value

    def LogProc(self, name, requirements):
        args = [name, requirements]
        message = {'subject': 'target.apparatus.LogProc', 'args': args}
        self.node.send('appa', message)

    def findDevice(self, reqs):
        # Build expected reply
        ereply = {}
        ereply['subject'] = 'target.apparatus.recv_value'
        ereply['args'] = ['devFound', 'e_reply']

        # Build primary message
        args = [reqs]
        message = {
            'subject': 'target.apparatus.findDevice',
            'args': args,
            'ereply': ereply,
        }
        self.loopBlocks['devFound'] = False
        self.node.send('appa', message)
        while not self.loopBlocks['devFound']:
            self.node.listen('appa')
        return self.returnedValue

    def serialClone(self):
        # Build expected reply
        ereply = {}
        ereply['subject'] = 'target.apparatus.recv_value'
        ereply['args'] = ['clone', 'e_reply']

        # Build primary message
        message = {'subject': 'target.apparatus.serialClone', 'ereply': ereply}
        self.loopBlocks['clone'] = False
        self.node.send('appa', message)
        while not self.loopBlocks['clone']:
            self.node.listen('appa')
        return self.returnedValue

    def applyTemplate(self, tName, args=None, kwargs=None):
        if kwargs is None:
            kwargs = {}
        if args is None:
            args = []
        margs = [tName]
        mkwargs = {'args': args, 'kwargs': kwargs}
        message = {
            'subject': 'target.apparatus.applyTemplate',
            'args': margs,
            'kwargs': mkwargs,
        }
        self.node.send('appa', message)

    def logApparatus(self, fname):
        margs = [fname]
        message = {'subject': 'target.apparatus.logApparatus', 'args': margs}
        self.node.send('appa', message)


class ExecutorInterface:
    def __init__(self, node):
        self.node = node
        self.devicelist = {}
        self.loopBlocks = {}
        self.localDefault = True

    def execute(self, eproclist):
        message = {'subject': 'target.executor.execute', 'args': [eproclist]}
        self.node.send('procexec', message)

    def createDevice(self, devName, devType, exec_address, rel_address):
        # Handle local creation of a device
        if self.node.name == rel_address:
            self.devicelist[devName] = {}
            self.devicelist[devName]['Address'] = getattr(Devices, devType)(devName)
            self.devicelist[devName]['AddressType'] = 'pointer'
            self.devicelist[devName]['Address'].executor = self
        else:
            ereply = {}
            ereply['subject'] = 'target.executor.recv_value'
            ereply['args'] = ['devMade', 'e_reply']

            # Build primary message
            args = [devName, devType, exec_address, rel_address]
            message = {
                'subject': 'target.executor.createDevice',
                'args': args,
                'ereply': ereply,
            }
            self.loopBlocks['devMade'] = False
            self.node.send(exec_address, message)
            while not self.loopBlocks['devMade']:
                self.node.listen(exec_address)

    def getDescriptors(self, device, address):
        # Build expected reply
        ereply = {}
        ereply['subject'] = 'target.executor.recv_value'
        ereply['args'] = ['gotDescriptors', 'e_reply']

        # Build primary message
        message = {
            'subject': 'target.executor.devicelist["'
            + device
            + '"]["Address"].getDescriptors',
            'ereply': ereply,
        }
        self.loopBlocks['gotDescriptors'] = False
        self.node.send(address, message)
        while not self.loopBlocks['gotDescriptors']:
            self.node.listen(address)
        return self.returnedValue

    def setSimulation(self, device, value, address):
        args = [value]
        message = {
            'subject': 'target.executor.devicelist["'
            + device
            + '"]["Address"].setSimulation',
            'args': args,
        }
        self.gotDescriptors = False
        self.node.send(address, message)

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
        # Build expected reply
        ereply = {}
        ereply['subject'] = 'target.executor.recv_value'
        ereply['args'] = ['gotDependence', 'e_reply']

        # Build primary message
        message = {
            'subject': 'target.executor.devicelist["'
            + device
            + '"]["Address"].getDependence',
            'ereply': ereply,
        }
        self.loopBlocks['gotDependence'] = False
        self.node.send(address, message)
        while not self.loopBlocks['gotDependence']:
            self.node.listen(address)
        return self.returnedValue

    def getDependencies(self, device, address):
        # Build expected reply
        ereply = {}
        ereply['subject'] = 'target.executor.recv_value'
        ereply['args'] = ['gotDependencies', 'e_reply']

        # Build primary message
        message = {
            'subject': 'target.executor.devicelist["'
            + device
            + '"]["Address"].getDependencies',
            'ereply': ereply,
        }
        self.loopBlocks['gotDependencies'] = False
        self.node.send(address, message)
        while not self.loopBlocks['gotDependencies']:
            self.node.listen(address)
        return self.returnedValue

    def recv_value(self, target, value):
        self.loopBlocks[target] = True
        self.returnedValue = value

    def getRequirements(self, device, eproc, address):
        # Build expected reply
        ereply = {}
        ereply['subject'] = 'target.executor.recv_value'
        ereply['args'] = ['gotRequirements', 'e_reply']

        # Build primary message
        args = [device, eproc, address]
        message = {
            'subject': 'target.executor.getRequirements',
            'args': args,
            'ereply': ereply,
        }
        self.loopBlocks['gotRequirements'] = False
        self.node.send(address, message)
        while not self.loopBlocks['gotRequirements']:
            self.node.listen(address)
        return self.returnedValue

    def getDevices(self, address):
        # Build expected reply
        ereply = {}
        ereply['subject'] = 'target.executor.recv_value'
        ereply['args'] = ['gotDevices', 'e_reply']

        # Build primary message
        args = [address]
        message = {
            'subject': 'target.executor.getDevices',
            'args': args,
            'ereply': ereply,
        }
        self.loopBlocks['gotDevices'] = False
        self.node.send(address, message)
        while not self.loopBlocks['gotDevices']:
            self.node.listen(address)
        return self.returnedValue

    def getEprocs(self, device, address):
        # Build expected reply
        ereply = {}
        ereply['subject'] = 'target.executor.recv_value'
        ereply['args'] = ['gotEprocs', 'e_reply']

        # Build primary message
        args = [device, address]
        message = {
            'subject': 'target.executor.getEprocs',
            'args': args,
            'ereply': ereply,
        }
        self.loopBlocks['gotEprocs'] = False
        self.node.send(address, message)
        while not self.loopBlocks['gotEprocs']:
            self.node.listen(address)
        return self.returnedValue

    def do(self, device, procedure, requirements):
        margs = [device, procedure, requirements]
        message = {'subject': 'target.do', 'args': margs}
        self.node.send('procexec', message)

    def doProc(self, index):
        margs = [index]
        message = {'subject': 'target.doProc', 'args': margs}
        self.node.send('procexec', message)

    def doProclist(self):
        message = {'subject': 'target.doProclist'}
        self.node.send('procexec', message)

    def getProclist(self):
        # Build expected reply
        ereply = {}
        ereply['subject'] = 'target.executor.recv_value'
        ereply['args'] = ['gotProclist', 'e_reply']

        # Build primary message
        message = {'subject': 'target.getProclist', 'ereply': ereply}
        self.loopBlocks['gotProclist'] = False
        self.node.send('procexec', message)
        while not self.loopBlocks['gotProclist']:
            self.node.listen('procexec')
        return self.returnedValue

    def clearProclist(self):
        message = {'subject': 'target.clearProclist'}
        self.node.send('procexec', message)

    def insertProc(self, index, device, procedure, requirements):
        margs = [index, device, procedure, requirements]
        message = {'subject': 'target.insertProc', 'args': margs}
        self.node.send('procexec', message)

    def updateProc(self, index, requirements):
        margs = [index, requirements]
        message = {'subject': 'target.updateProc', 'args': margs}
        self.node.send('procexec', message)

    def removeProc(self, index):
        margs = [index]
        message = {'subject': 'target.removeProc', 'args': margs}
        self.node.send('procexec', message)

    def swapProcs(self, index1, index2):
        margs = [index1, index2]
        message = {'subject': 'target.swapProcs', 'args': margs}
        self.node.send('procexec', message)
