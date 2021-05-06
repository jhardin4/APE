# blank

# Only import 'basic' python packages up here.  All others should be imported
# within the methods.

# Handle the different relative locations for independently running and
#
import time

from Devices import Sensor


class Keyence_GT2_A3200(Sensor):
    def __init__(self, name):
        Sensor.__init__(self, name)
        self.returnformat = ''
        self.A3200handle = ''
        self.DOaxis = ''  # ZZ1
        self.DObit = ''  # 0
        self.AIaxis = ''  # ZZ2
        self.AIchannel = ''  # 0
        self.axis = 'ZZ2'
        self.dependent_device = True
        self.dependencies = ['A3200', 'system']
        self.extend_delay = 1
        self.extended = False
        self.def_num_points = 5

        # used during initialization, take more samples
        self.init_number = 10
        self.init_delay = 0.1

        # used during movement, take less samples
        self.fast_number = 3
        self.fast_delay = 0.01
        self.min_step = 0.01
        self.speed = 10
        self.step = 1  # note, bad things may happen if this gets too big

        # machine parameters
        self.z_window = 1
        self.v_window = 4
        self.extend_delay = 1
        self.safe_positions = dict(ZZ1=0, ZZ2=0, ZZ3=0, ZZ4=0)
        self.configured = False
        self.sampleresult = 0
        self.zresult = 0

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
        self.requirements['Connect']['AIaxis'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'AI axis on A3200',
        }
        self.requirements['Connect']['AIchannel'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'channel on the AI axis being used',
        }

        self.requirements['Initialize'] = {}
        self.requirements['Initialize']['num_points'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'I dont really know what this number is for',
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
        AIaxis='',
        AIchannel='',
        systemname='',
        systemaddress='',
    ):
        self.descriptors.append(A3200name)
        self.A3200handle = self.checkDependencies(A3200name, A3200address)
        self.axis = axis
        self.DOaxis = DOaxis
        self.DObit = DObit
        self.AIaxis = AIaxis
        self.AIchannel = AIchannel
        self.systemname = systemname
        self.systemhandle = self.checkDependencies(systemname, systemaddress)

        self.addlog(
            'Keyence Touchprobe using '
            + A3200name
            + ' using '
            + str(self.DOaxis)
            + ' bit '
            + str(self.DObit)
        )
        return self.returnlog()

    def Initialize(self, num_points=''):
        if num_points == '':
            num_points = self.def_num_points

        if num_points < 2:
            num_points = 2

        # Calibration routine
        if not self.simulation:
            import numpy as np

            datavessel = [0]
            self.set_voltage_window()
            v = []
            z = []
            v_target = [
                self.v_low + i * (self.v_high - self.v_low) / (num_points + 1)
                for i in range(1, num_points + 1)
            ]

            self.extend()
            self.goto_contact()
            for value in v_target:
                self.goto_voltage(value, step=self.z_window / num_points)
                self.wait_for_settle(timing='normal')
                self.sample(10, 1)
                v.append(self.sampleresult)
                self.addlog(
                    self.A3200handle.getPosition(
                        address=datavessel, addresstype='pointer', axislist=[self.axis]
                    )
                )
                z.append(datavessel[0][0])

            # use the z and v arrays to get the slope, then calculate the reference z
            p = np.polyfit(v, z, 1)
            self.dzdv = p[0]
            # loglines += self.get_z() + '\n'
            # self.ref_position[self.axis] = self.zresult

            self.configured = True
            self.addlog('Height to voltage slope is ' + str(self.dzdv))
        else:
            self.addlog('Initialization done.')
        return self.returnlog()

    def set_voltage_window(self, n=100, t=5):
        '''
        Extend and retract the probe to get the voltage window
            (and test if the extension is working.)
        '''
        vi = 0
        vf = 0

        self.retract()
        self.addlog(self.systemhandle.Dwell(dtime=0.5))
        self.wait_for_settle(timing='slow')
        self.sample(n, t)
        vi = self.sampleresult
        self.extend()
        self.addlog(self.systemhandle.Dwell(dtime=0.5))
        self.wait_for_settle(timing='slow')
        self.sample(n, t)
        vf = self.sampleresult
        self.v_high = vi
        self.v_low = vf
        self.retract()
        self.addlog('Voltage window set to ' + str(vi) + ' to ' + str(vf))

    def Measure(self, address='', addresstype='', retract=True):
        '''
        Take a measurement.
        '''
        if not self.simulation:
            datavessel = [0]
            self.addlog(
                self.A3200handle.getAI(
                    address=datavessel,
                    addresstype='pointer',
                    axis=self.AIaxis,
                    channel=self.AIchannel,
                )
            )
            if datavessel[0] > 0.8 * self.v_high:
                self.extend()
                self.addlog(self.systemhandle.Dwell(dtime=0.25))
                self.wait_for_settle()
            self.sample(3, 0.05)
            if not (1.2 * self.v_low < self.sampleresult < 1.8 * self.v_high):
                self.goto_contact()
            self.goto_voltage(
                (self.v_high + self.v_low) / 2,
                step=self.z_window / 2,
                diff=0.35 * (self.v_high - self.v_low),
            )
            self.wait_for_settle()
            self.get_z()
            result = self.zresult
        else:
            result = float(input('What is the expected height?'))

        if retract:
            self.retract()
        self.StoreMeasurement(address, addresstype, result)
        return self.returnlog()

    def wait_for_settle(self, limit=0.01, timeout=5, timing='normal'):
        '''
        Wait for the probe to settle prior to a measurement.
        '''
        timing_values = {'slow': [20, 0.2], 'normal': [10, 0.1], 'fast': [5, 0.05]}
        if timing not in timing_values.keys():
            timing = 'normal'
        self.sample(*timing_values[timing], average=False)
        v = self.sampleresult
        start = time.time()
        while (max(v) - min(v) > limit) and (time.time() - start < timeout):
            self.sample(*timing_values[timing], average=False)
            v = self.sampleresult
        self.addlog(
            'Voltage settled in '
            + str((time.time() - start) * 1000)
            + ' ms at '
            + timing
            + ' rate'
        )

    def sample(self, n, t, average=True):
        v = 0
        vlist = []
        datavessel = [0]
        if not self.simulation:
            for i in range(n):
                self.addlog(
                    self.A3200handle.getAI(
                        address=datavessel,
                        addresstype='pointer',
                        axis=self.AIaxis,
                        channel=self.AIchannel,
                    )
                )
                v += datavessel[0]
                vlist.append(datavessel[0])
                time.sleep(t / n)
            if average:
                self.sampleresult = v / n
            else:
                self.sampleresult = vlist
        else:
            if average:
                v_string = input('What is the average voltage reading in volts?')
                self.sampleresult = float(v_string)
            else:
                vmax_string = input('What is the max voltage reading in volts?')
                vmin_string = input('What is the min voltage reading in volts?')
                vlist = [float(vmax_string), float(vmin_string)]
                self.sampleresult = vlist

        self.addlog('The following voltages were measured: \n' + str(vlist))

    def goto_contact(self):
        '''
        Moves down rapidly untill the GT2 makes contact. Should be used with care to avoid collisions.
        '''
        datavessel = [0]
        self.addlog(self.A3200handle.Set_Motion(RelAbs='Rel', motionmode='cmd'))
        self.addlog(
            self.A3200handle.getAI(
                address=datavessel,
                addresstype='pointer',
                axis=self.AIaxis,
                channel=self.AIchannel,
            )
        )
        voltage = datavessel[0]
        self.addlog(
            self.A3200handle.getPosition(
                address=datavessel, addresstype='pointer', axislist=[self.axis]
            )
        )
        z_current = datavessel[0][0]
        while voltage < 1.1 * self.v_low:
            # take steps until the voltage changes from the min (extended) value
            cur_position = z_current
            z_current -= self.step

            point = {self.axis: -self.step}
            self.addlog(
                self.A3200handle.Move(
                    point=point,
                    motiontype='incremental',
                    speed=self.speed,
                    motionmode='cmd',
                )
            )
            while z_current + 0.5 * self.step < cur_position:
                # wait for more than half the step to be taken
                self.addlog(
                    self.systemhandle.Dwell(dtime=self.step / (5.0 * self.speed))
                )
                self.addlog(
                    self.A3200handle.getPosition(
                        address=datavessel, addresstype='pointer', axislist=[self.axis]
                    )
                )
                cur_position = datavessel[0][0]
            self.addlog(
                self.A3200handle.getAI(
                    address=datavessel,
                    addresstype='pointer',
                    axis=self.AIaxis,
                    channel=self.AIchannel,
                )
            )
            voltage = datavessel[0]

        # step back up half a step to account for overshoot and to wait for the move to complete
        point = {self.axis: 0.5 * self.step}
        self.addlog(
            self.A3200handle.Move(
                point=point,
                motiontype='incremental',
                speed=self.speed,
                motionmode='cmd',
            )
        )
        self.addlog(self.systemhandle.Dwell(dtime=self.step / (self.speed)))

    def goto_voltage(self, v, step=0.25, diff=0.05):
        '''
        Move the axis until the touch-probe output is v +/- diff.
        '''
        direction = 0
        # test the voltage first to decide on a direction
        self.addlog(self.A3200handle.Set_Motion(RelAbs='Rel', motionmode='cmd'))
        self.wait_for_settle(limit=0.005, timeout=1, timing='fast')
        self.sample(3, 0.03)
        current_v = self.sampleresult
        while not (v - diff < current_v < v + diff):
            # print(v - diff, '<', current_v, '<', v + diff)
            if v - diff > current_v:
                direction = -1
            else:
                direction = 1
            point = {self.axis: direction * step}
            self.addlog(
                self.A3200handle.Move(
                    point=point, motiontype='linear', speed=self.speed, motionmode='cmd'
                )
            )
            self.wait_for_settle(limit=0.005, timeout=1, timing='fast')
            self.sample(3, 0.03)
            current_v = self.sampleresult
            # check to see if we're chainging directions
            if v - diff > current_v:
                new_direction = -1
            else:
                new_direction = 1
            if direction * new_direction < 0:
                step = step / 2.0

    def get_z(self, n=5, t=0.1):
        '''
        Sample the analog input and axis position to get the correct position.
        '''
        self.sample(n, t)
        v = self.sampleresult
        datavessel = [0]
        self.addlog(
            self.A3200handle.getPosition(
                address=datavessel, addresstype='pointer', axislist=[self.axis]
            )
        )
        z = datavessel[0][0]
        self.last_v = v
        self.last_z = z
        self.zresult = z - self.dzdv * v

    def retract(self):
        self.addlog(
            self.A3200handle.Set_DO(
                axis=self.DOaxis, bit=self.DObit, value=0, motionmode='cmd'
            )
        )
        self.extended = False

    def extend(self):
        self.addlog(
            self.A3200handle.Set_DO(
                axis=self.DOaxis, bit=self.DObit, value=1, motionmode='cmd'
            )
        )
        self.extended = True
