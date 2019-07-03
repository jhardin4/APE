# This Device represents a computer, typically the one everything is being
# run on. Currently, most of the explicit timing is run through a System.

# Only import 'basic' python packages up here.  All others should be imported
# within the methods.
import time

from Devices import Device
from importlib import import_module


class System(Device):
    def __init__(self, name):
        # Run the Device initialization.
        Device.__init__(self, name)
        # Run simulation is controlled by its own
        # Append relevant descriptors
        self.descriptors.append('system')
        # Defining the elemental procedures
        self.requirements['Dwell'] = {}
        self.requirements['Dwell']['dtime'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'time to wait in seconds',
        }

        self.requirements['Run'] = {}
        self.requirements['Run']['address'] = {
            'value': '',
            'source': 'direct',
            'address': '',
            'desc': 'address of the program or pointer to it',
        }
        self.requirements['Run']['addresstype'] = {
            'value': '',
            'source': 'direct',
            'address': '',
            'desc': 'type of address',
        }
        self.requirements['Run']['arguments'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'list of the arguments for the program in order. Will be decomposed with * operator',
        }

    def Dwell(self, dtime=''):
        if not self.simulation and dtime != '':
            time.sleep(dtime)
        self.addlog(self.name + ' waited ' + str(dtime) + ' s.')

        return self.returnlog()

    def Run(self, address='', addresstype='pointer', arguments=None):
        # This elemental procedure runs a function but does not capture its
        # return.
        # The address and address type allow targeting a specific function.
        # The arguments are decomposed from a list, therefore, there is order
        # dependence.
        # THESE WILL RUN IN SIMULATION MODE!!
        if arguments is None:
            arguments = []
        if addresstype == 'pointer':
            addList = address.split('.')
            base = import_module(addList[0])
            if len(addList) > 1:
                for n in range(1, len(addList)):
                    base = getattr(base, addList[n])
            base(*arguments)
        progdesc = str(address)
        self.addlog(self.name + ' ran a program, ' + progdesc)

        return self.returnlog()


if __name__ == '__main__':

    def testFunction(message):
        print(message)

    print('Demonstrating "real" mode')
    mySystem = System('mySystem')
    log = ''
    log += mySystem.Connect()
    log += mySystem.Dwell(dtime=1)
    log += mySystem.Run(
        address=testFunction, addresstype='pointer', arguments=['test message']
    )
    log += mySystem.Disconnect()
    print('... and the resulting log.')
    print(log)
    print('Demonstrating "simulation" mode')
    mySystem.simulation = True
    log = ''
    log += mySystem.Connect()
    log += mySystem.Dwell(dtime=1)
    log += mySystem.Run(
        address=testFunction, addresstype='pointer', arguments=['test message']
    )
    log += mySystem.Disconnect()
    print('... and the resulting log.')
    print(log)
