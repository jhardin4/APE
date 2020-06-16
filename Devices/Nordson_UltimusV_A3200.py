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
        self.defaulttask = 3
        self.dependencies = ['A3200']

        self.requirements['Connect']['A3200name'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'name of the A3200 controller being used',
        }
        self.requirements['Connect']['A3200address'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'pointer to the A3200 device',
        }
        self.requirements['Connect']['IOaxis'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'IO axis on A3200',
        }
        self.requirements['Connect']['IObit'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'bit on the IO axis being used',
        }

    def On(self, task='', mode='cmd'):
        if task == '':
            task = self.defaulttask
        self.addlog(self.A3200handle.Set_DO(
                axis=self.IOaxis, 
                bit=self.IObit, 
                value=1, 
                task=task, 
                motionmode=mode
                ))
        self.on = True
        self.addlog(self.name + ' is on.')
        return self.returnlog()

    def Off(self, task='', mode='cmd'):
        if task == '':
            task = self.defaulttask
        self._Off(task=task, mode=mode)
        return self.returnlog()

    def _Off(self, task='', mode='cmd'):
        # This method exists to allow initializing to off in Connect
        self.addlog(self.A3200handle.Set_DO(
                axis=self.IOaxis, 
                bit=self.IObit, 
                value=0, 
                task=task, 
                motionmode=mode
                ))
        self.on = False
        self.addlog(self.name + ' is off.')
        
    def Connect(
        self,
        A3200name='',
        A3200address='',
        IOaxis='',
        IObit='',
        COM= ''
    ):
        Nordson_UltimusV.Connect(self, COM)
        self.descriptors.append(A3200name)
        self.A3200handle = self.checkDependencies(A3200name, A3200address)
        self.IOaxis = IOaxis
        self.IObit = IObit

        self.addlog(f'{self.name} is connected using {self.IOaxis} bit {self.IObit} on {A3200name}')
        # Resets the bit just in case it was already on.
        self._Off(self.defaulttask, 'cmd')

        return self.returnlog()
