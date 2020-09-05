# This Device represents a general G-Code motion system.

# Only import 'basic' python packages up here.  All others should be imported
# within the methods.

# Handle the different relative locations for independently running and
#
from Devices import Sensor
from Devices import Motion
import time


class Aerotech_A3200_RoboDaddy(Motion, Sensor):
    def __init__(self, name):
        Motion.__init__(self, name)

        self.descriptors = list({*self.descriptors, 'Aerotech', 'A3200', 'sensor'})

        self.tasklog = {'task1': [], 'task2': [], 'task3': [], 'task4': []}
        self.commandlog = []
        self.defaulttask = 1
        self.handle = ''

        # Possible modes are cmd and loadrun
        self.axes = [
            'X',
            'Y',
            'A',
            'B',
            'C',
            'D',
        ]
        self.axismask = {}
        self.maxaxis = 4

        self.requirements['Set_Motion']['task'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'task being used for this operation',
        }
        self.requirements['Set_Motion']['length_units'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'length units for motion',
        }
        self.requirements['Set_Motion']['MotionRamp'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'Ramp rate for a set of coordinated motions',
        }
        self.requirements['Set_Motion']['MaxAccel'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'Maximum acceleration during coordinated motion',
        }
        self.requirements['Set_Motion']['LookAhead'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'Activate multi-command motion planning',
        }
        self.requirements['Set_Motion']['axismask'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'how to convert between target and machine dimensions',
        }
        self.requirements['Set_Motion']['dtask'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'default task',
        }

        self.requirements['Move'] = {}
        self.requirements['Move']['point'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'Information about where to move to',
        }
        self.requirements['Move']['motiontype'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'kind of path taken to point',
        }
        self.requirements['Move']['speed'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'speed of the motion',
        }
        self.requirements['Move']['task'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'task being used for this operation',
        }
        self.requirements['Move']['motionmode'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'cmd or loadrun to determine if it si stored in a buffer, commandlog, or run immediately',
        }

        self.requirements['set_DO'] = {}
        self.requirements['set_DO']['axis'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'IO axis',
        }
        self.requirements['set_DO']['bit'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'bit on IO axis',
        }
        self.requirements['set_DO']['value'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'value of that bit.  0 or 1',
        }

        self.requirements['Run'] = {}
        self.requirements['Run']['task'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'Which task buffer to run',
        }

        self.requirements['getPosition'] = {}
        self.requirements['getPosition']['address'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'Address of where to store result',
        }
        self.requirements['getPosition']['addresstype'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'Type of address',
        }
        self.requirements['getPosition']['axislist'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'List of axes that will be reported',
        }

        self.requirements['getAI'] = {}
        self.requirements['getAI']['address'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'Address of where to store result',
        }
        self.requirements['getAI']['addresstype'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'Type of address',
        }
        self.requirements['getAI']['axis'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'Axis of AI',
        }
        self.requirements['getAI']['channel'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'Channel on that axis',
        }

        self.requirements['Load'] = {}
        self.requirements['Load']['cmstr'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'String of commands to load',
        }
        self.requirements['Load']['task'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'task being used for this operation',
        }
        self.requirements['Load']['mode'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'cmd or loadrun to determine if it si stored in a buffer, commandlog, or run immediately',
        }

        self.requirements['LogData_Start'] = {}
        self.requirements['LogData_Start']['file'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'Where to store results',
        }
        self.requirements['LogData_Start']['points'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'Maximum number of points to collect',
        }
        self.requirements['LogData_Start']['parameters'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': '{axis: [pc, pf, vc, vf, ac, af]...}',
        }
        self.requirements['LogData_Start']['interval'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'cmd or loadrun to determine if it si stored in a buffer, commandlog, or run immediately',
        }
        self.requirements['LogData_Start']['task'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'task being used for this operation',
        }
        self.requirements['LogData_Start']['mode'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'cmd or loadrun to determine if it si stored in a buffer, commandlog, or run immediately',
        }

        self.requirements['LogData_Stop'] = {}
        self.requirements['LogData_Stop']['task'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'task being used for this operation',
        }
        self.requirements['LogData_Stop']['mode'] = {
            'value': '',
            'source': 'apparatus',
            'address': '',
            'desc': 'cmd or loadrun to determine if it si stored in a buffer, commandlog, or run immediately',
        }

    def Connect(self):
        if not self.simulation:
            from Devices.Drivers import A3200_RoboDaddy

            self.handle = A3200_RoboDaddy.A3200()
        self.addlog(self.name + ' is connected')

        return self.returnlog()

    def Disconnect(self):
        if not self.simulation:
            self.handle.disconnect()
        self.addlog(Motion.Disconnect(self))

        return self.returnlog()

    def Set_Motion(
        self,
        dtask='',
        axismask='',
        length_units='',
        RelAbs='',
        MotionRamp='',
        MaxAccel='',
        LookAhead='',
        dmotionmode='',
        dmotiontype='',
        motionmode='',
        task='',
    ):
        # These direct assignments are somewhat queue jumping at the moment
        if dtask != '':
            self.defaulttask = dtask

        if dmotiontype != '':
            self.motiontype = dmotiontype

        if dmotionmode != '':
            self.motionmode = dmotionmode

        if task == '':
            task = self.defaulttask

        if motionmode == '':
            motionmode = self.motiontype

        # These do not que jump
        if axismask != '':
            self.fSet_axismask(axismask, task, motionmode)

        if RelAbs != '':
            self.fSet_RelAbs(RelAbs, task, motionmode)

        if length_units != '':
            self.fSet_length_units(length_units, task, motionmode)

        if MotionRamp != '':
            self.fSet_MotionRamp(MotionRamp, task, motionmode)

        if MaxAccel != '':
            self.fSet_MaxAccel(MaxAccel, task, motionmode)

        if LookAhead != '':
            self.fSet_LookAhead(LookAhead, task, motionmode)

        return self.returnlog()

    def fSet_axismask(self, axismask, task, motionmode, update=False):
        if update:
            self.axismask = axismask
            self.addlog('Axis mask changed to ' + str(self.axismask))
        else:
            kwargs = {
                'axismask': axismask,
                'task': task,
                'motionmode': motionmode,
                'update': True,
            }
            self.tasklog['task' + str(task)].append(
                {'function': self.fSet_axismask, 'args': kwargs}
            )

        self.fRun(motionmode, task)

    def fSet_LookAhead(self, LookAhead, task, motionmode):
        if LookAhead:
            self.tasklog['task' + str(task)].append('VELOCITY ON \n')
        else:
            self.tasklog['task' + str(task)].append('VELOCITY OFF \n')
        self.motionsetting['LookAhead'] = LookAhead

        self.fRun(motionmode, task)

    def fSet_MaxAccel(self, MaxAccel, task, motionmode):
        self.tasklog['task' + str(task)].append(
            'CoordinatedAccelLimit = ' + str(MaxAccel) + '\n'
        )
        self.motionsetting['MaxAccel'] = MaxAccel
        self.fRun(motionmode, task)

    def fSet_RelAbs(self, RelAbs, task, motionmode):
        if RelAbs == 'Rel':
            self.tasklog['task' + str(task)].append('G91 \n')

        if RelAbs == 'Abs':
            self.tasklog['task' + str(task)].append('G90 \n')

        self.motionsetting['RelAbs'] = RelAbs
        self.fRun(motionmode, task)

    def fSet_MotionRamp(self, MotionRamp, task, motionmode):
        self.tasklog['task' + str(task)].append('RAMP RATE ' + str(MotionRamp) + '\n')

        self.motionsetting['MotionRamp'] = MotionRamp
        self.fRun(motionmode, task)

    def fSet_length_units(self, length_units, task, motionmode):
        if length_units == 'mm':
            self.tasklog['task' + str(task)].append('G71 \n')

        if length_units == 'inch':
            self.tasklog['task' + str(task)].append('G70 \n')

        self.motionsetting['length_units'] = length_units
        self.fRun(motionmode, task)

    def Set_DO(self, axis='', bit='', value='', task='', motionmode=''):
        if motionmode == '':
            motionmode = self.motionmode

        if task == '':
            task = self.defaulttask

        if not self.simulation:
            cmdstr = '$DO' + '[' + str(bit) + '].' + axis + ' = ' + str(value) + ' \n'
            self.tasklog['task' + str(task)].append(cmdstr)
        self.addlog(
            'Bit ' + str(bit) + ' on the ' + str(axis) + ' set to ' + str(value)
        )

        self.fRun(motionmode, task)

        return self.returnlog()

    def Move(self, point='', motiontype='', speed='', task='', motionmode=''):
        if task == '':
            task = self.defaulttask
        self.tasklog['task' + str(task)].append(
            {'function': self.MotionCMD, 'args': [point, speed, motiontype]}
        )

        self.fRun(motionmode, task)
        return self.returnlog()

    def MotionCMD(self, point, speed, motiontype):
        if motiontype == '':
            motiontype = self.motiontype
        cmdline = ''

        for dim in self.axismask:
            if dim in point:
                point[self.axismask[dim]] = point[dim]
                point.pop(dim, None)

        if motiontype == 'linear':
            axescount = 0
            cmdline += 'G01 '
            for axis in self.axes:
                if axis in point:
                    axescount += 1
                    if axescount > self.maxaxis:
                        # print(cmdline)
                        raise Exception('Number of axes exceeds ITAR limit.')
                    cmdline += axis + ' ' + '{0:f}'.format(point[axis]) + ' '
            cmdline += 'F ' + '{0:f}'.format(speed) + ' '
            cmdline += '\n'

        if motiontype == 'incremental':
            cmdline += 'MOVEINC '
            axis = list(point)[0]
            cmdline += (
                axis + ' ' + '{0:f}'.format(point[axis]) + ' ' + '{0:f}'.format(speed)
            )
            cmdline += '\n'

        self.addlog(cmdline)

        return cmdline

    def Run(self, task=''):
        self.fRun('cmd', task)

        return self.returnlog()

    def fRun(self, motionmode, task):
        if task == '':
            task = self.defaulttask

        if motionmode == '':
            motionmode = self.motionmode
        if motionmode == 'loadrun':
            self.addlog('Commands Loaded')
        elif motionmode == 'cmd':
            self.commandlog = self.tasklog['task' + str(task)]
            self.tasklog['task' + str(task)] = []
            cmdline = self.commandlog
            self.sendCommands(cmdline, task)
            self.commandlog = []

    def getPosition(self, address='', addresstype='', axislist=''):
        if addresstype == '':
            addresstype = 'pointer'
        result = 'No postion collected'
        # Get the postion from the driver
        if not self.simulation:
            result = self.handle.get_position(axislist)

        # Store it at the target location
        self.StoreMeasurement(address, addresstype, result)
        self.log += str(axislist) + ' measured to be ' + str(result)

        return self.returnlog()

    def getAI(self, address='', addresstype='', axis='', channel=''):
        # Get the postion from the driver
        if not self.simulation:
            result = self.handle.AI(axis, channel)
        else:
            rstring = input(
                'What is the simulated value for '
                + str(axis)
                + ' '
                + str(channel)
                + '?'
            )
            result = float(rstring)

        # Store it at the target location
        self.StoreMeasurement(address, addresstype, result)
        self.log = (
            'AI Axis '
            + str(axis)
            + ' channel '
            + str(channel)
            + ' measured to be '
            + str(result)
        )

        return self.returnlog()

    def sendCommands(self, commands, task):

        cmdmessage = ''
        for line in commands:
            if type(line) == str:
                cmdmessage += line
                self.addlog(line)
            elif type(line) == dict and line['function'] == self.MotionCMD:
                cmdmessage += line['function'](*line['args'])
            elif type(line) == dict:
                line['function'](**line['args'])
        if not self.simulation:
            # print(cmdmessage)
            self.handle.cmd_exe(cmdmessage, task=task)
    
    def gen_cal_table(self, start_point, x_length, y_length, x_count, y_count, outaxis, result, file=''):
        '''
        Generate calibration table from grid of measurements
        '''

        import os
        import numpy as np
        filename = os.getcwd() + "\\" + file

        spacing = [x_length/(x_count-1),y_length/(y_count-1)]
        offset = start_point.values()
        
        outaxis = self.axes.index(outaxis)+2

        if outaxis == 7:
            outputaxis3 = 7 #If 4th Z-axis is selected, use the 4th.
        else:
            outputaxis3 = 6 #Default output axis 3 to 3rd Z-axis

        header = """'        RowAxis  ColumnAxis  OutputAxis1  OutputAxis2  SampDistRow  SampDistCol  NumCols
:START2D    2          1           4            5           {1:.6f}          -{0:.6f}       {2}
:START2D OUTAXIS3={3} POSUNIT=PRIMARY CORUNIT=PRIMARY/1000 OFFSETROW=-{5:.6f} OFFSETCOL={4:.6f} NEGCOR\n""".format(*spacing,x_count,outputaxis3,*offset)

        footer = """:END
'
'
' Notes:
' Assume X is axis 1, Y axis 2, A axis 4, B axis 5, {0} axis {1} in this example.
' The ColumnAxis (X) moves along a given row, selecting a particular column based on the SampDistCol
' setting (-{2:.6f} mm in this example).
' The RowAxis (Y) moves vertically in the table, selecting a particular row of correction values based
' on the SampDistRow setting ({3:.6f} mm in this example).
' OutputAxis1 ({4}) gets correction from the first element of each correction triplet.
' OutputAxis2 ({5}) gets correction from the second element of each correction triplet.
' OutputAxis3 ({0}) gets correction from the third element of each correction triplet""".format(self.axes[outputaxis3-2],outputaxis3,*spacing,*self.axes[2:4])

        # Correct around last position measured
        scan = result-result.flatten()[-1]
        
        # Convert mm reading to microns
        scan *= 1000

        # Add zeros
        output = np.zeros((scan.shape[0],scan.shape[1]*3))

        if outaxis == 7:
            replacement_col = 2
        else:
            replacement_col = outaxis-4
            
        for i in range(scan.shape[1]):
            output[:,i*3+replacement_col] = scan[:,i]

        # Write table to outfile
        f=open(filename,'w')
        f.write(header)
        np.savetxt(f,output,fmt='%.3f')
        f.write(footer)
        f.close()

        return self.returnlog()

    def enableCalTable(self, file='',task=''):
        '''
        Load and enable calibration table on A3200 controller.
        '''
        # Load calibration table to controller
        import os
        filename = os.getcwd() + "\\" + file
        self.sendCommands('LOADCALFILE "{}", 2D_CAL'.format(filename),task=task)
        self.tasklog['task' + str(task)].append('2D calibration table at ' + filename + ' loaded to controller.')
        # Enable calibration table
        self.sendCommands('CALENABLE 2D',task=task)
        self.tasklog['task' + str(task)].append('2D calibration table has been enabled.')
        return self.returnlog()
    
    def disableCalTable(self,task=''):
        '''
        Disable calibration table on A3200 controller.
        '''
        self.sendCommands('CALDISABLE 2D',task=task)
        self.tasklog['task' + str(task)].append('2D calibration table has been disabled.')
        return self.returnlog()

    def LogData_Start(
        self, file='', points='', parameters='', interval='', task='', motionmode=''
    ):
        if task == '':
            task = self.defaulttask
        self.tasklog['task' + str(task)].append(
            'DATACOLLECT STOP\nDATACOLLECT ITEM RESET\n'
        )
        index = 0
        for dim in parameters:
            if type(parameters[dim]) == list:
                for element in parameters[dim]:
                    temp = 'DATACOLLECT ITEM %s, %s, DATAITEM_' % (str(index), dim)
                    if element[0] == 'p':
                        temp += 'Position'
                    elif element[0] == 'v':
                        temp += 'Velocity'
                    elif element[0] == 'a':
                        temp += 'Acceleration'
                    else:
                        raise Exception(dim + str(element) + ' is an unknown parameter')

                    if element[1] == 'f':
                        temp += 'Feedback'
                    elif element[1] == 'c':
                        temp += 'Command'
                    else:
                        raise Exception(dim + str(element) + ' is an unknown parameter')
                    self.tasklog['task' + str(task)].append(temp + '\n')
                    index += 1
        import os

        filename = os.getcwd() + '\\' + file
        self.tasklog['task' + str(task)].append(
            '$task[0] = FILEOPEN "%s" , 0\n' % (filename)
        )
        self.tasklog['task' + str(task)].append(
            'DATACOLLECT START $task[0], %s, %s\n' % (str(points), str(interval))
        )
        self.fRun(motionmode, task)
        return self.returnlog()

    def LogData_Stop(self, task='', motionmode=''):
        if task == '':
            task = self.defaulttask
        self.tasklog['task' + str(task)].append(
            'DATACOLLECT STOP\nFILECLOSE $task[0]\n'
        )
        self.fRun(motionmode, task)
        return self.returnlog()


if __name__ == '__main__':
    myA3200 = Aerotech_A3200_RoboDaddy('myA3200')
    myA3200.simulation = True
