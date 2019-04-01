# Parent class of all Devices
# Put all methods that should be shared amoung all Devices here

# Only import 'basic' python packages up here.  All others should be imported
# within the methods.


class Device():
    def __init__(self, name):
        # Set the default simulation state of the Device
        # For complex simulation behavor, this could have multiple components
        self.simulation = False
        # Defines if the Device is connected to its target
        self.connected = False
        # Sets the name of a this instance of the Device
        self.name = name
        # Create and instance of the descriptor list.  These strings can be used 
        self.descriptors = []
        # Define if this device is a composite of other Devices
        self.dependent_device = False
        self.dependencies = []
        # Initialize the elemental procedure requirements dictionary
        self.requirements = {}
        # Description of information need to do each elemental procedure
        # Only methods in this dictionary can be accessed by APE
        self.requirements['On'] = {}
        self.requirements['Off'] = {}
        self.requirements['Set'] = {}
        # Each input of an elemental procedure needs to be defined
        # 'value' is a place holder for the value being used.  It is only here
        # for historical reasons at the moment.
        # 'source' designates where to get this value from.  Typically this
        # will be 'apparatus' if it is going to fetch the value from the
        # apparatus using and apparatus address or 'direct' if this value is
        # going to be directly given to the elemental procedure.  This might
        # be redundant.
        # 'address' is typically an apparatus address for use when 'source' is
        # apparatus.
        # 'desc' is a description of what this information is.
        self.requirements['Set']['setting'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'example setting'}
        self.requirements['Connect'] = {}
        self.requirements['Disconnect'] = {}
        # Initialize the log string
        self.log = ''
        # Information for handling connections
        self.apparatus_connection = 'pointer'

    def On(self):
        # Example of turning the device on
        self.addlog(self.name + ' on')
        if not self.simulation:
            print(self.name + ' is on.')

        return self.returnlog()

    def Off(self):
        # Example of turning the device off
        self.addlog(self.name + ' off')
        if not self.simulation:
            print(self.name + ' is off.')

        return self.returnlog()

    def Set(self, setting=''):
        # Example of setting the device
        self.addlog(self.name + ' set to ' + str(setting))
        if not self.simulation:
            print(self.name + ' is set to ' + str(setting))

        return self.returnlog()

    def getDescriptors(self):
        return self.descriptors

    def setSimulation(self, value):
        self.simulation = value

    def getDependence(self):
        return self.dependent_device

    def getDependencies(self):
        return self.dependencies

    def getRequirements(self, eproc):
        return list(self.requirements[eproc])

    def CreateEprocs(self, apparatus, executor):
        # Go through all the elemental procedures of the Device and register
        # each with the Apparatus as an elemental procedure
        # Imports are 'hidden' in the methods to enabel independent function
        # This assume that this method is called from the root APE directory!
        from Core import Procedure
        for eleproc in self.requirements:
            class eproc(Procedure):
                def Prepare(myself):
                    myself.device = self.name
                    myself.method = eleproc
                    myself.requirements = self.requirements[eleproc]
                    myself.executor = executor
                    myself.name = 'eproc_'+myself.device+'_'+myself.method

                def Plan(myself):
                    details = {}
                    for req in myself.requirements:
                        details[req] = myself.requirements[req]['value']

                    myself.executor.execute([[{
                            'devices': myself.device,
                            'procedure': myself.method,
                            'details': details
                            }]])
            # Create the entry used to to access the elemental procedure later
            eprocEntry = {
                    'device': self.name,
                    'method': eleproc,
                    'handle': eproc(apparatus, executor)
                    }
            apparatus['eproclist'].append(eprocEntry)

    def returnlog(self):
        # Returns the current device log and clears it
        # This is largely for communicating with the Executor
        # Eventually this will need to actually communicate with message
        # passing.
        message = self.log
        self.log = ''

        return message

    def addlog(self, logstr):
        # Add to the log string
        # This allows methods that are not elemental procedures to contribute
        # to the log.
        self.log += logstr + '\n'

    def ERegister(self, executer):
        # Register a particular device with the executor
        executer.loadDevice(self.name, self, 'pointer')

    def Connect(self):
        # Example of connecting the device
        self.addlog(self.name + ' is connected.')
        if not self.simulation:
            print(self.name + ' is connected.')

        return self.returnlog()

    def Disconnect(self):
        # Example of disconnecting the device
        self.addlog(self.name + ' is disconnected.')
        if not self.simulation:
            print(self.name + ' is disconnected.')

        return self.returnlog()


# For testing and debuging
if __name__ == '__main__':
    myDevice = Device('myDevice')
    print('Demonstrating "real" mode')
    log = ''
    log += myDevice.Connect()
    log += myDevice.Set(setting='Good')
    log += myDevice.On()
    log += myDevice.Off()
    log += myDevice.Disconnect()
    print('... and the resulting log.')
    print(log)
    print('Demonstrating "simulation" mode')
    myDevice.simulation = True
    log = ''
    log += myDevice.Connect()
    log += myDevice.Set(setting='Good')
    log += myDevice.On()
    log += myDevice.Off()
    log += myDevice.Disconnect()
    print('... and the resulting log.')
    print(log)    
