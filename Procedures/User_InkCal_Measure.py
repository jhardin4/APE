from Core import Procedure
import Procedures.Pump_PumpOn
import Procedures.Pump_PumpOff
import Procedures.Motion_RefRelPriorityLineMotion
import Procedures.Aerotech_A3200_Set
import json
import time


class User_InkCal_Measure(Procedure):
    def Prepare(self):
        self.name = 'User_InkCal_Measure'
        self.requirements['material'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'parameters used to generate toolpath',
        }
        self.requirements['filename'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'name of alignmentfile',
        }
        self.requirements['filename']['address'] = ['information', 'calibrationfile']
        self.requirements['time'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'name of alignmentfile',
        }
        self.requirements['time']['address'] = [
            'information',
            'ink calibration',
            'time',
        ]
        self.pmotion = Procedures.Motion_RefRelPriorityLineMotion(
            self.apparatus, self.executor
        )
        self.pumpon = Procedures.Pump_PumpOn(self.apparatus, self.executor)
        self.pumpoff = Procedures.Pump_PumpOff(self.apparatus, self.executor)
        self.userinput = Procedures.User_Consol_Input(self.apparatus, self.executor)
        self.motionset = Procedures.Aerotech_A3200_Set(self.apparatus, self.executor)
        self.useroptions = Procedures.User_Consol_InputOptions(
            self.apparatus, self.executor
        )

    def Plan(self):
        # Reassignments for convienence
        material = self.requirements['material']['value']
        filename = self.requirements['filename']['value']
        ptime = self.requirements['time']['value']

        # FIND devices needed for procedure
        motion = self.apparatus.findDevice(descriptors=['motion'])
        system = self.apparatus.findDevice(descriptors=['system'])
        _ = self.apparatus.findDevice(descriptors=['nozzle', material])
        pump = self.apparatus.findDevice(descriptors=['pump', material])

        self.pmotion.requirements['axismask']['address'] = [
            'devices',
            motion,
            'n' + material,
            'axismask',
        ]
        self.pmotion.requirements['refpoint']['address'] = [
            'information',
            'alignments',
            'n' + material + '@cal',
        ]
        self.pmotion.requirements['speed']['address'] = [
            'devices',
            motion,
            'default',
            'speed',
        ]

        # Do stuff
        # Go to calibration position
        self.motionset.Do({'Type': 'default'})
        self.pmotion.Do({'priority': [['Z'], ['X', 'Y']]})
        self.DoEproc(motion, 'Run', {})

        # Get intial information
        initialweightok = False
        while not initialweightok:
            message = 'What is the initial weight of the slide in grams?'
            default = ''
            self.userinput.Do({'message': message, 'default': default})
            initialweightstr = self.userinput.response
            try:
                initialweight = float(initialweightstr)
                message = 'Is ' + initialweightstr + 'g the correct value?(y/n)'
                options = ['y', 'n']
                default = 'y'
                self.useroptions.Do(
                    {'message': message, 'options': options, 'default': default}
                )
                confirmation = self.useroptions.response
                if confirmation == 'y':
                    initialweightok = True
            except ValueError:
                print('That is not a number.  Try again.')
        message = 'Put slide in place and press ENTER.'
        default = ''
        self.userinput.Do({'message': message, 'default': default})

        # turn pumps on and off
        pressure = self.apparatus.getValue(['devices', pump, 'pressure'])
        self.DoEproc(pump, 'Set', {'pressure': pressure})
        self.pumpon.Do({'pump_name': pump})
        self.DoEproc(system, 'Dwell', {'dtime': ptime})
        self.pumpoff.Do({'pump_name': pump})

        finalweightok = False
        while not finalweightok:
            message = 'What is the final weight of the slide in grams?'
            default = ''
            self.userinput.Do({'message': message, 'default': default})
            finalweightstr = self.userinput.response
            try:
                finalweight = float(finalweightstr)
                message = 'Is ' + str(finalweightstr) + 'g the correct value?(y/n)'
                options = ['y', 'n']
                default = 'y'
                self.useroptions.Do(
                    {'message': message, 'options': options, 'default': default}
                )
                confirmation = self.useroptions.response
                if confirmation == 'y':
                    finalweightok = True
            except ValueError:
                print('That is not a number.  Try again.')

        # Construct the data entry for the calibration log
        dataline = {
            'delta_weight': finalweight - initialweight,
            'test_time': ptime,
            'time': time.time(),
        }
        cfilename = material + filename
        # Load in the previous file
        with open(cfilename, 'r') as caljson:
            file_data = json.load(caljson)
        file_data.append(dataline)
        # Store the updated data
        with open(cfilename, 'w') as caljson:
            json.dump(file_data, caljson)
        with open(
            'Logs/' + str(int(round(time.time(), 0))) + cfilename, 'w'
        ) as caljson:
            json.dump(file_data, caljson)
