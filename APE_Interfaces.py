# These are interfaces that simplify communication between
class ApparatusInterface():
    def __init__(self):
        self.valueReceived = True
        self.returnedValue = 0
        self.node = ''
        self.apparatus_address = ''

    def Connect_All(self, executor, simulation=False):
        args = [executor]
        kwargs = {'simulation': app_address}
        message = {'subject': 'target.apparatus.Connect_All', 'args': args, 'kwargs': kwargs}
        self.node.send('apparatus', message)        
        
    def setValue(self, app_address, value):
        kwargs = {'infoAddress': app_address, 'value': value}
        message = {'subject': 'target.apparatus.setValue', 'kwargs': kwargs}
        self.node.send('apparatus', message)
    
    
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
        message = {'subject': 'target.apparatus.getValue', 'kwargs': kwargs, 'ereply': ereply}
        self.valueReceived = False
        self.node.send('apparatus', message)
        while not self.valueReceived:
            self.node.listen('appa')
        return self.returnedValue

    def returnValue(self, value):
        self.valueReceived = True
        self.returnedValue = value

    def LogProc(self, name, requirements):
        args = [name, requirments]
        message = {'subject': 'target.apparatus.LogProc', 'args': args}
        self.node.send('apparatus', message)


class ExecutorInterface():
    def __init__(self):
        self.node = ''
        self.apparatus_address = ''

    def execute(self, eproclist):
        message = {'subject': 'target.executor.execute', 'args': [eproclist]}
        self.node.send('procexec', message)


class DeviceInterface():
    def __init__(self):
        self.loopBlocks = {}
        self.gotDescriptors = True
        self.gotRequirements = True
        self.gotDependence = True
        self.gotDependencies = True
        self.devMade = True
        self.returnedValue = 0
        self.node = ''
        self.apparatus_address = ''

    def createDevice(self, devName, devType, devAddressType):
        #Build expected reply
        ereply = {}
        ereply['subject'] = 'target.device_interface.recv_value'
        ereply['args'] = ['devMade', 'e_reply']

        # Build primary message
        args = [devName, devType, devAddressType]
        message = {'subject': 'target.executor.createDevice',
                   'args':args,
                   'ereply': ereply}
        self.loopBlocks['devMade'] = False
        self.node.send('procexec', message)
        while not self.loopBlocks['devMade']:
            self.node.listen('procexec')       
        
    def getDescriptors(self, device):
        #Build expected reply
        ereply = {}
        ereply['subject'] = 'target.device_interface.recv_value'
        ereply['args'] = ['gotDescriptors', 'e_reply']

        # Build primary message
        message = {'subject': 'target.executor.devicelist.' + device + '.Address.getDescriptors', 'ereply': ereply}
        self.loopBlocks['gotDescriptors'] = False
        self.node.send('procexec', message)
        while not self.loopBlocks['gotDescriptors']:
            self.node.listen('procexec')
        return self.returnedValue
    
    def setSimulation(self, device, value):
        args=[value]
        message = {'subject': 'target.executor.devicelist.' + device + '.Address.setSimulation', 'args':args}
        self.gotDescriptors = False
        self.node.send('procexec', message)

    def getRequirements(self, device, eproc):
        #Build expected reply
        ereply = {}
        ereply['subject'] = 'target.device_interface.recv_value'
        ereply['args'] = ['gotRequirements', 'e_reply']

        # Build primary message
        args = [eproc]
        message = {'subject': 'target.executor.devicelist.' + device + '.Address.getRequirements', 'args':args, 'ereply': ereply}
        self.loopBlocks['gotRequirements'] = False
        self.node.send('procexec', message)
        while not self.loopBlocks['gotRequirements']:
            self.node.listen('procexec')
        return self.returnedValue

    def getDependence(self, device):
        #Build expected reply
        ereply = {}
        ereply['subject'] = 'target.device_interface.recv_value'
        ereply['args'] = ['gotDependence', 'e_reply']

        # Build primary message
        message = {'subject': 'target.executor.devicelist.' + device + '.Address.getDependence', 'ereply': ereply}
        self.loopBlocks['gotDependence'] = False
        self.node.send('procexec', message)
        while not self.loopBlocks['gotDependence']:
            self.node.listen('procexec')
        return self.returnedValue
    
    def getDependencies(self, device):
        #Build expected reply
        ereply = {}
        ereply['subject'] = 'target.device_interface.recv_value'
        ereply['args'] = ['gotDependencies', 'e_reply']

        # Build primary message
        message = {'subject': 'target.executor.devicelist.' + device + '.Address.getDependencies', 'ereply': ereply}
        self.loopBlocks['gotDependencies'] = False
        self.node.send('procexec', message)
        while not self.loopBlocks['gotDependencies']:
            self.node.listen('procexec')
        return self.returnedValue        
    
    def recv_value(self, target, value):
        self.loopBlocks[target] = True
        self.returnedValue = value
    