from Devices import Sensor

class Keyence_LS7010_A3200(Sensor):
    """
    The Keyence LS7010 micrometer array functions through serial communication
    coupled with a digital output to control a bank of relays (see driver for 
    more details).
    """

    def __init__(self, name):
        Sensor.__init__(self, name)
        self.A3200handle = ''
        self.DOaxis = ''  # X
        self.DObit = ''  # 7
        self.dependent_device = True
        self.dependencies = ['A3200', 'system']

        # Variables to store state
        self.XY_active = None

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
        self.requirements['Connect']['COM'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'Serial COM port to communcate through',
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
        self.requirements['Measure']['mode'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'whether to measure "XY" position of "Z" position',
        }


    def Connect(
        self,
        A3200name='',
        A3200address='',
        axis='',
        DOaxis='',
        DObit='',
        systemname='',
        systemaddress='',
        COM='',
    ):
        self.descriptors.append(A3200name)
        self.A3200handle = A3200address
        self.axis = axis
        self.DOaxis = DOaxis
        self.DObit = DObit
        self.systemname = systemname
        self.systemhandle = systemaddress

        if not self.simulation:
            from Devices.Drivers import keyence_LS7010
            self.handle = keyence_LS7010.KeyenceLS7010(COM)

        self.addlog(
            'Keyence Micrometer array connected using '
            + A3200name
            + ' with '
            + str(self.DOaxis)
            + ' bit '
            + str(self.DObit)
            + 'DO to switch sensor head,'
            + ' using COM'
            + str(COM)
            + 'to communicate over serial.'
        )
        return self.returnlog()

    def Measure(self, mode, address='', addresstype=''):
        if not self.simulation:
            if mode.upper() == 'XY':
                self.switch_XY()
                result = self.handle.get_xy()
                
            elif mode.upper() == 'Z':
                self.switch_Z()
                result = self.handle.get_z()
            else:
                raise ValueError("Mode incorrectly specified")
        else:
            result = float(input('What is the expected position?'))
        self.StoreMeasurement(address, addresstype, result)
        self.addlog('Micrometer' + self.name + ' measured a weight of ' + result)
    
    def switch_XY(self):
        '''
        Switch relay bank and program on micrometer to XY reading mode.
        '''
        if not self.XY_active:
            self.handle.xy_mode()
        self.addlog(
            self.A3200handle.Set_DO(
                axis=self.DOaxis, bit=self.DObit, value=0, motionmode='cmd'
            )
        )
        self.XY_active = True

    def switch_Z(self):
        '''
        Switch relay bank and program on micrometer to Z reading mode.
        '''
        if self.XY_active:
            self.handle.z_mode()
        self.addlog(
            self.A3200handle.Set_DO(
                axis=self.DOaxis, bit=self.DObit, value=1, motionmode='cmd'
            )
        )
        self.XY_active = True