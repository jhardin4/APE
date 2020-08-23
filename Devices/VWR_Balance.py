from Devices import Sensor

class VWR_Balance(Sensor):
    def __init__(self, name):
        Sensor.__init__(self, name)
        self.descriptors = [
            *self.descriptors,
            *['balance', 'weight', 'VWR', 'P2'],
        ]
        self.requirements['Connect']['COM'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'Serial COM port to communcate through',
        }
        self.requirements['Measure'] = {}
        self.requirements['Measure']['address'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'address to store value',
        }
        self.requirements['Measure']['addresstype'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'addres type of address',
        }
        self.requirements['Measure']['stable'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'whether balance should wait to stabilize before sending reading',
        }
        self.driver_address = ''
        self.name = name

    def Connect(self, COM=''):
        """ Connect to balance.
        """
        if not self.simulation:
            from Devices.Drivers import vwr_balance
            self.handle = vwr_balance.VWRBalance(COM)
        
        self.addlog('Balance ' + self.name + ' is connected on port ' + str(COM))

    def Disconnect(self):
        """ Stop connection to balance.
        """
        if not self.simulation:
            self.handle.disconnect()
            self.addlog('Balance ' + self.name + ' is disconnected.')

    def Tare(self):
        """ Tare balance.
        """
        if not self.simulation:
            self.handle.tare()
        self.addlog('Balance ' + self.name + ' has been tared.')

    def Zero(self):
        """ Zero balance.
        """
        if not self.simulation:
            self.handle.zero()
        self.addlog('Balance ' + self.name + ' has been zeroed.')

    def Measure(self, address='', addresstype='', stable=True):
        """ Take a measurement from the balance.
            Reading can be specified to be either a stable (True)
            or unstable (False)reading using the 'stable' argument.
        """
        if not self.simulation:
            if stable:
                result = self.handle.stable_measure()
            else:
                result = self.handle.measure()
        else:
            result = float(input('What is the expected weight'))
        self.StoreMeasurement(address, addresstype, result)
        self.addlog('Balance ' + self.name + ' measured a weight of ' + result)