# blank
# Only import 'basic' python packages up here.  All others should be imported
# within the methods.

# Handle the different relative locations for independently running and
#

from Devices import Pump
import threading


class Nordson_UltimusV(Pump):
    def __init__(self, name):
        Pump.__init__(self, name)
        self.descriptors = [
            *self.descriptors,
            *['pump', 'pressure', 'Nordson', 'Ultimus', 'UltimusV'],
        ]

        self.requirements['Connect']['COM'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'Serial COM port to communcate through',
        }
        self.requirements['Set']['pressure'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'pressure when the pump is ON',
        }
        self.requirements['Set']['vacuum'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'vacuum when the pump is OFF',
        }
        self.requirements['DelayedOn'] = {}
        self.requirements['DelayedOn']['delay'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'time to wait before turning on pump',
        }
        self.requirements['DelayedOff'] = {}
        self.requirements['DelayedOff']['delay'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'time to wait before turning off pump',
        }
        self.pressure = 0
        self.vacuum = 0
        self.driver_address = ''

    def On(self):
        if not self.simulation:
            self.driver_address.startPump()
        self.on = True
        self.addlog(self.name + ' is on.')

        return self.returnlog()

    def Off(self):
        if not self.simulation:
            self.driver_address.stopPump()
        self.on = False
        self.addlog(self.name + ' is off.')

        return self.returnlog()

    def DelayedOn(self, delay):
        if not self.simulation:
            t = threading.Timer(delay, self.driver_address.startPump)
        else:
            t = threading.Timer(delay, print, ['Pump On'])
        t.start()
        self.addlog(self.name + ' will turn on in ' + str(delay) + ' s.')
        self.on = True
        return self.returnlog()

    def DelayedOff(self, delay):
        if not self.simulation:
            t = threading.Timer(delay, self.driver_address.stopPump)
        else:
            t = threading.Timer(delay, print, ['Pump Off'])
        t.start()
        self.addlog(self.name + ' will turn off in ' + str(delay) + ' s.')
        self.on = False
        return self.returnlog()

    def Connect(self, COM=''):
        if not self.simulation:
            from Devices.Drivers import Ultimus_V as UltimusV

            self.driver_address = UltimusV.Ultimus_V_Pump(COM)

        self.addlog('Ultimus ' + self.name + ' is connected on port ' + str(COM))

        return self.returnlog()

    def Set(self, pressure='', vacuum=''):
        if pressure != '':
            if not self.simulation:
                self.driver_address.set_pressure(pressure)
            self.pressure = pressure
        if vacuum != '':
            if not self.simulation:
                self.driver_address.set_vacuum(vacuum)
            self.vacuum = vacuum
        self.addlog(
            self.name
            + ' is set to '
            + str(pressure)
            + 'kPa pressure and '
            + str(vacuum)
            + 'kPa vacuum.'
        )

        return self.returnlog()

    def Disconnect(self):
        if not self.simulation:
            if self.driver_address != '':
                self.driver_address.disconnect()

        self.addlog(Pump.Disconnect(self))

        return self.returnlog()
