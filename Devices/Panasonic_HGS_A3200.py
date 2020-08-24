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
        self.backstep_dist = 0.5
        self.measure_speed = 0.01
        self.extend_delay = 2
        self.reading_gvariable = 4
        self.move_to_floor = -200
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

        self.requirements['grid'] = {}
        self.requirements['grid']['start_point'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'starting position of scan (lower left)',
        }
        self.requirements['grid']['start_point'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'starting position of scan (lower left pos)',
        }
        self.requirements['grid']['x_length'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'length of the scanning grid in x axis',
        }
        self.requirements['grid']['y_length'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'length of the scanning grid in y axis',
        }
        self.requirements['grid']['x_count'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'number of measurement points along x axis',
        }
        self.requirements['grid']['y_count'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'number of measurement points along y axis',
        }
        self.requirements['grid']['address'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'address to store value',
        }
        self.requirements['grid']['addresstype'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'addres type of address',
        }

        self.requirements['gen_cal_table'] = {}
        self.requirements['gen_cal_table']['outfile'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'location on drive to save calibration table',
        }

        self.requirements['enable_cal_table'] = {}
        self.requirements['enable_cal_table']['infile'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'location of calibration table to load',
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
        self.A3200handle = A3200address
        self.axis = axis
        self.DOaxis = DOaxis
        self.DObit = DObit
        self.DIaxis = DIaxis
        self.DIbit = DIbit
        self.systemname = systemname
        self.systemhandle = systemaddress

        self.addlog(
            'Keyence Touchprobe using '
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
            self.A3200handle.cmd_exe("PROBE INPUT PROBE_INPUT_DRIVE_DIGITAL X " + str(self.DIbit))
            self.addlog('Probe input set to axis ' + str(self.DIaxis) + ' and bit ' + str(self.DIbit))
            # Probe mode setting
            self.A3200handle.cmd_exe("PROBE MODE PROBE_SW_MODE 1 $global[{}]".format(self.reading_gvariable))
            self.addlog('Probe mode set to 1 with output saved to $global[{}]'.format(self.reading_gvariable))
        else:
            self.addlog('Initialization done.')
        return self.returnlog()

    def Measure(self, address='', addresstype='', retract=True):
        '''
        Take a measurement.
        '''
        if not self.simulation:
            # Extend probe
            self.extend()
            self.addlog(self.systemhandle.Dwell(dtime= self.extend_delay))
            
            # Start monitoring probe
            self.A3200handle.cmd_exe("PROBE ON {}".format(self.axis))
            self.addlog('Probe monitoring turned on for axis ' + self.axis)

            # Slowly move probe down, it will stop when probe fault is triggered
            point = {self.axis: self.move_to_floor}
            self.addlog(
                self.A3200handle.Move(
                    point=point,
                    motiontype='incremental',
                    speed=self.slow_speed,
                    motionmode='cmd',
                )
            )

            # Waits for the probe input to capture and write the axis positions.
            self.A3200handle.cmd_exe("WAIT ((TASKSTATUS(DATAITEM_TaskStatus0) & TASKSTATUS0_ProbeCycle) == 0) -1")      

            # Backstep, moving up then back down again for slower measurement
            point = {self.axis: self.backstep_dist}
            self.addlog(
                self.A3200handle.Move(
                    point=point,
                    motiontype='incremental',
                    speed=self.backstep_speed,
                    motionmode='cmd',
                )
            )

            # Turn on probe monitoring again
            self.A3200handle.cmd_exe("PROBE ON {}".format(self.axis))
            self.addlog('Probe monitoring turned on for axis ' + self.axis)

            # Slowly move probe down rest of the way, will stop when triggered
            point = {self.axis: self.move_to_floor}
            self.addlog(
                self.A3200handle.Move(
                    point=point,
                    motiontype='absolute',
                    speed=self.measure_speed,
                    motionmode='cmd',
                )
            )

            # Waits for the probe input to capture and write the axis positions.
            self.A3200handle.cmd_exe("WAIT ((TASKSTATUS(DATAITEM_TaskStatus0) & TASKSTATUS0_ProbeCycle) == 0) -1")      

            result = self.A3200handle.get_global_variable(self.reading_gvariable)
        else:
            result = float(input('What is the expected height?'))

        if retract:
            # Retract probe
            self.retract()

        self.latest_reading = result
        self.StoreMeasurement(address, addresstype, result)
        self.addlog('Displacement Sensor ' + self.name + ' measured a position of ' + str(result))

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

    def grid(self, start_point, x_length, y_length, x_count, y_count, address='', addresstype='', travel_dist=5):
        '''
        Take grid of measurements.
        '''
        self.start_point = start_point
        self.x_length = x_length
        self.y_length = y_length
        self.x_count = int(x_count)
        self.y_count = int(y_count)

        grid_results = []
        if not self.simulation:
            for y_pos in np.linspace(start_point['y'],start_point['u']+y_length,endpoint=True):
                for x_pos in np.linspace(start_point['x'],start_point['x']+x_length,endpoint=True):
                    # Move to grid point
                    point = {'X': x_pos, 'Y': y_pos}
                    self.addlog(
                        self.A3200handle.Move(
                            point=point,
                            motiontype='absolute',
                            speed=self.measure_speed,
                            motionmode='cmd',
                        )
                    )
                    # Measure using probe
                    self.Measure(address,addresstype,retract = False)
                    grid_results.append(self.measure_reading)

                    # Move up to translate to next position
                    point = {self.axis: travel_dist}
                    self.addlog(
                        self.A3200handle.Move(
                            point=point,
                            motiontype='incremental',
                            speed=self.fast_speed,
                            motionmode='cmd',
                        )
                    )

            self.grid_reading = np.reshape(grid_results,(self.y_count,self.x_count))
        
    def gen_cal_table(self, outfile, outaxis):
        '''
        Generate cal table that can be applied to Aerotech stage.
        Note: Need to add in reading offset between probe and printhead in order to 
            appropriately shift the table for the acutal print head.
        '''
        spacing = [self.x_length/(self.x_count-1),self.y_length/(self.y_count-1)]
        header = """
        '        RowAxis  ColumnAxis  OutputAxis1  OutputAxis2  SampDistRow  SampDistCol  NumCols
        :START2D    2          1           4            5           {0}          -{1}       {2}
        :START2D OUTAXIS3={3} POSUNIT=PRIMARY CORUNIT=PRIMARY/1000 OFFSETROW=-{4} OFFSETCOL={5}
        :START2D NEGCOR SERIALNUMBER="164764"\n
        """.format(*spacing,self.y_count,int(outaxis),*offset)

        footer = """
        :END
        '
        '
        ' Notes:
        ' Assume X is axis 1, Y axis 2, D axis 3 in the above example. 
        ' The ColumnAxis (X) moves along a given row, selecting a particular column based on the SampDistCol
        ' setting (-12.5 mm in this example).
        ' The RowAxis (Y) moves vertically in the table, selecting a particular row of correction values based
        ' on the SampDistRow setting (12.5 mm in this example).
        ' OutputAxis1 (X) gets correction from the first element of each correction triplet.
        ' OutputAxis2 (Y) gets correction from the second element of each correction triplet.
        ' OutputAxis3 (D) gets correction from the third element of each correction triplet
        """

        scan = self.grid_reading
        # Correct from min position
        scan -= np.min(scan)
        # Convert mm reading to microns
        scan *= 1000

        # Add zeros
        output = np.zeros((scan.shape[0],scan.shape[1]*3))
        for i in range(scan.shape[1]):
            output[:,i*3+2] = scan[:,i]

        # Write table to outfile
        f=open(outfile,'w')
        f.write(header)
        np.savetxt(f,output,fmt='%.3f')
        f.write(footer)
        f.close()

    def enable_cal_table(self, infile):
        '''
        Load and enable calibration table on A3200 controller.
        '''
        # Load calibration table to controller
        self.A3200handle.cmd_exe('LOADCALFILE "{}", 2D_CAL'.format(infile))
        self.addlog('2D calibration table at ' + infile + ' loaded to controller.')
        # Enable calibration table
        self.A3200handle.cmd_exe('CALENABLE 2D')
        self.addlog('2D calibration table has been enabled.')

    def disable_cal_table(self):
        '''
        Disable calibration table on A3200 controller.
        '''
        self.A3200handle.cmd_exe('CALDISABLE 2D')
        self.addlog('2D calibration table has been disabled.')