# blank 

# Only import 'basic' python packages up here.  All others should be imported
# within the methods.

# Handle the different relative locations for independently running and
#

from Devices import Nordson_UltimusV


class Nordson_UltimusV_A3200(Nordson_UltimusV):
    def __init__(self, name):
        Nordson_UltimusV.__init__(self, name)

        self.descriptors.append('A3200')

        self.pressure = 0
        self.vacuum = 0
        self.pumphandle = ''
        self.A3200handle = ''
        self.IOaxis = ''
        self.IObit = ''
        self.dependent_device = True
        self.defaulttask = 1
        self.dependencies = ['pump', 'A3200']

        self.requirements['Connect']['pumpname'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'name of the pump being used'}
        self.requirements['Connect']['pumpaddress'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'pointer to the pump device'}
        self.requirements['Connect']['A3200name'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'name of the A3200 controller being used'}
        self.requirements['Connect']['A3200address'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'pointer to the A3200 device'}
        self.requirements['Connect']['IOaxis'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'IO axis on A3200'}
        self.requirements['Connect']['IObit'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'bit on the IO axis being used'}

        # This entry is removed because the pump should already be connected
        self.requirements['Connect'].pop('COM', None)

    def On(self, task='', mode='cmd'):
        self.log += self.A3200handle.Set_DO(axis=self.IOaxis, bit=self.IObit, value=1, task=task, motionmode=mode)
        self.on = True
        self.addlog(self.name + ' is on.')
        return self.returnlog()

    def Off(self, task='', mode='cmd'):
        self.fOff(task, mode)
        return self.returnlog()

    def Set(self, pressure='', vacuum=''):
        self.addlog(self.pumphandle.Set(pressure=pressure, vacuum=vacuum))
        return self.returnlog()

    def fOff(self, task, mode):
        self.log += self.A3200handle.Set_DO(axis=self.IOaxis, bit=self.IObit, value=0, task=task, motionmode=mode)
        self.on = False
        self.addlog(self.name + ' is off.')

    def Connect(self, pumpname='', A3200name='', pumpaddress='', A3200address='', IOaxis = '', IObit = ''):
        self.descriptors.append(pumpname)
        self.descriptors.append(A3200name)
        self.pumphandle = pumpaddress
        self.A3200handle = A3200address
        self.IOaxis = IOaxis
        self.IObit = IObit

        self.addlog('Ultimus/A3200 ' + pumpname +
                    '/' + A3200name +
                    ' ' + self.name +
                    ' is connected using ' + str(self.IOaxis) +
                    ' bit ' + str(self.IObit))
        self.fOff(self.defaulttask, 'cmd')

        return self.returnlog()
   
