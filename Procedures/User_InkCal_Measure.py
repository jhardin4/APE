from Core import Procedure
import Procedures.Pump_PumpOn
import Procedures.Pump_PumpOff
import Procedures.Motion_RefRelPriorityLineMotion
import json
import time


class User_InkCal_Measure(Procedure):
    def Prepare(self):
        self.name = 'User_InkCal_Measure'
        self.requirements['material'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'parameters used to generate toolpath'}
        self.requirements['filename'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'name of alignmentfile'}
        self.requirements['filename']['address'] = ['information', 'calibrationfile']
        self.pmotion = Procedures.Motion_RefRelPriorityLineMotion(self.apparatus, self.executor)
        self.pumpon = Procedures.Pump_PumpOn(self.apparatus, self.executor)
        self.pumpoff = Procedures.Pump_PumpOff(self.apparatus, self.executor)

    def Plan(self):
        # Reassignments for convienence
        material = self.requirements['material']['value']
        filename = self.requirements['filename']['value']

        # FIND devices needed for procedure
        motion = self.apparatus.findDevice({'descriptors': ['motion']})
        system = self.apparatus.findDevice({'descriptors': ['system']})
        nozzle = self.apparatus.findDevice({'descriptors': ['nozzle', material]})
        pump = self.apparatus.findDevice({'descriptors': ['pump', material]})

        #Find elemental procedures
        run = self.apparatus.GetEproc(motion, 'Run')
        dwell = self.apparatus.GetEproc(system, 'Dwell')
        pumpset = self.apparatus.GetEproc(pump, 'Set')
        
        self.pmotion.requirements['axismask']['address'] = ['devices', motion, 'n'+material, 'axismask']
        self.pmotion.requirements['refpoint']['address'] = ['information', 'alignments', 'n'+material+'@cal']
        self.pmotion.requirements['speed']['address'] = ['devices', motion, 'default', 'speed']

        # Do stuff
        # Go to calibration position
        self.pmotion.Do({'priority': [['Z'], ['X', 'Y']]})
        run.Do()

        # Get intial information
        initialweightok = False
        while not initialweightok:
            initialweightstr = input('What is the initial weight of the slide in grams?')
            try:
                initialweight = float(initialweightstr)
                qtext = 'Is ' + initialweightstr + 'g the correct value?(y/n)'
                confirmation = input(qtext)
                if confirmation == 'y':
                    initialweightok = True
            except ValueError:
                print('That is not a number.  Try again.')
        input('Put slide in place and press ENTER.')

        # turn pumps on and off
        ptime = self.apparatus['information']['ink calibration']['time']
        pumpset.requirements['pressure']['address'] = ['devices', pump, 'pressure']
        pumpset.Do()
        self.pumpon.Do({'name': pump})
        dwell.Do({'dtime': ptime})
        self.pumpoff.Do({'name': pump})

        finalweightok = False
        while not finalweightok:
            finalweightstr = input('What is the final weight of the slide in grams?')
            try:
                finalweight = float(finalweightstr)
                qtext = 'Is ' + str(finalweightstr + 'g the correct value?(y/n)')
                confirmation = input(qtext)
                if confirmation == 'y':
                    finalweightok = True
            except ValueError:
                print('That is not a number.  Try again.')

        # Construct the data entry for the calibration log
        dataline = {'delta_weight': finalweight-initialweight, 'test_time': ptime, 'time': time.time()}
        cfilename = material + filename
        # Load in the previous file
        with open(cfilename, 'r') as caljson:
            file_data = json.load(caljson)
        file_data.append(dataline)
        # Store the updated data
        with open(cfilename, 'w') as caljson:
            json.dump(file_data, caljson)
        with open('Logs/' + str(int(round(time.time(), 0))) + cfilename, 'w') as caljson:
            json.dump(file_data, caljson)
