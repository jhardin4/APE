import numpy as np
from Devices import Sensor

class Panasonic_HGS_A3200(Sensor):
    def __init__(self, name):
        Sensor.__init__(self, name)
        self.A3200handle = ''
        self.DOaxis = ''  # X
        self.DObit = ''  # 0
        self.DIaxis = '' # X
        self.DIbit = '' # 1
        self.axis = 'D'
        self.name = name
        self.extended = False
        self.dependent_device = True
        self.dependencies = ['A3200', 'system']
        
        # Parameters defining probe behaviour
        self.fast_speed = 10
        self.slow_speed = 1
        self.backstep_speed = 0.1
        self.backstep_dist = 0.2
        self.measure_speed = 0.01
        self.extend_delay = 2
        self.reading_gvariable = 4
        self.latest_reading = None

        # Variables to store results
        self.measure_reading = None
        self.grid_reading = None

        # Elemental Procedures
        self.requirements['Connect']['A3200name'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'name of the system device',
        }
        self.requirements['Connect']['A3200address'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'pointer to the system device',
        }
        self.requirements['Connect']['systemname'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'name of the A3200 device',
        }
        self.requirements['Connect']['systemaddress'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'pointer to the A3200 device',
        }
        self.requirements['Connect']['axis'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'motion axis',
        }
        self.requirements['Connect']['DOaxis'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'DO axis on A3200',
        }
        self.requirements['Connect']['DObit'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'bit on the DO axis being used',
        }
        self.requirements['Connect']['DIaxis'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'DO axis on A3200',
        }
        self.requirements['Connect']['DIbit'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'bit on the DO axis being used',
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
            'desc': 'address type of address',
        }
        self.requirements['Measure']['retract'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'whether to retract the probe at end of measurement',
        }

    def Connect(
        self,
        A3200name='',
        A3200address='',
        axis='',
        DOaxis='',
        DObit='',
        DIaxis='',
        DIbit='',
        systemname='',
        systemaddress='',
    ):
        self.descriptors.append(A3200name)
        self.A3200handle = self.checkDependencies(A3200name, A3200address)
        self.axis = axis
        self.DOaxis = DOaxis
        self.DObit = DObit
        self.DIaxis = DIaxis
        self.DIbit = DIbit
        self.systemname = systemname
        self.systemhandle = self.checkDependencies(systemname, systemaddress)

        self.addlog(
            'Panasonic Touchprobe using '
            + A3200name
            + ' using '
            + str(self.DOaxis)
            + ' bit '
            + str(self.DObit)
            + 'to extend probe'
            + ' using '
            + str(self.DIaxis)
            + ' bit '
            + str(self.DIbit)
            + 'as probe digital input.'
        )
        return self.returnlog()

    def Initialize(self):
        '''
        Setting up the probe.
        '''
        if not self.simulation:
            # Probe input setup
            # Need to figure out how to get axis mask here
            self.A3200handle.sendCommands("PROBE INPUT PROBE_INPUT_DRIVE_DIGITAL X " + str(self.DIbit),task=1)
            self.addlog('Probe input set to axis ' + str(self.DIaxis) + ' and bit ' + str(self.DIbit))
            # Probe mode setting
            self.A3200handle.sendCommands("PROBE MODE PROBE_SW_MODE 1 $global[{}]".format(self.reading_gvariable),task=1)
            self.addlog('Probe mode set to 1 with output saved to $global[{}]'.format(self.reading_gvariable))
        else:
            self.addlog('Initialization done.')
        return self.returnlog()

    def Measure(self, address='', addresstype='', retract=True):
        '''
        Take a measurement.
        '''
        if not self.simulation:
            # Extend probe if not out
            if not self.extended:
                self.extend()
                self.addlog(self.systemhandle.Dwell(dtime= self.extend_delay))
            
            # Start monitoring probe and move down
            self.A3200handle.sendCommands("PROBE ON {0}\nFREERUN {0} -{1}\nWAIT ((TASKSTATUS(DATAITEM_TaskStatus0) & TASKSTATUS0_ProbeCycle) == 0) -1".format(self.axis,self.slow_speed),task=1)
            self.addlog('Probe monitoring turned on for axis ' + self.axis)

            # Backstep, moving up then back down again for slower measurement
            self.A3200handle.sendCommands("G91\nG01 {0}{1} F{2}\nG90".format(self.axis,self.backstep_dist,self.backstep_speed),task=1)

            # Turn on probe monitoring again and move down slower
            self.A3200handle.sendCommands("PROBE ON {0}\nFREERUN {0} -{1}\nWAIT ((TASKSTATUS(DATAITEM_TaskStatus0) & TASKSTATUS0_ProbeCycle) == 0) -1".format(self.axis,self.measure_speed),task=1)
            self.addlog('Probe monitoring turned on for axis ' + self.axis)
            
            # Turn off probe monitoring
            self.A3200handle.sendCommands("PROBE OFF",task=1)

            # Read result from temp global variable
            result = self.A3200handle.handle.get_global_variable(self.reading_gvariable)[0]
        else:
            result = float(input('What is the expected height?'))

        if retract:
            # Retract probe
            self.retract()

        self.latest_reading = result
        self.StoreMeasurement(address, addresstype, result)
        self.addlog('Displacement Sensor ' + self.name + ' measured a position of ' + str(result))
        return self.returnlog()

    def retract(self):
        '''
        Retract pneumatic probe.
        '''
        self.addlog(
            self.A3200handle.Set_DO(
                axis=self.DOaxis, bit=self.DObit, value=1, motionmode='cmd'
            )
        )
        self.extended = False

    def extend(self):
        '''
        Extend pneumatic probe.
        '''
        self.addlog(
            self.A3200handle.Set_DO(
                axis=self.DOaxis, bit=self.DObit, value=0, motionmode='cmd'
            )
        )
        self.extended = True