from Core import Procedure
import Procedures.User_InkCal_Calculate
import Procedures.User_InkCal_Measure
import json


class User_InkCal_Calibrate(Procedure):
    def Prepare(self):
        self.name = 'User_InkCal_Calibrate'
        self.requirements['material'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'parameters used to generate toolpath'}
        self.requirements['filename'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'name of alignmentfile'}
        self.requirements['filename']['address'] = ['information', 'calibrationfile']
        self.cal_calculation = Procedures.User_InkCal_Calculate(self.apparatus, self.executor)
        self.cal_measurement = Procedures.User_InkCal_Measure(self.apparatus, self.executor)
        self.useroptions = Procedures.User_Consol_InputOptions(self.apparatus, self.executor)

    def Plan(self):
        material = self.requirements['material']['value']
        filename = self.requirements['filename']['value']

        # Do stuff
        # Handle the first call of a calibration on a particular material
        # This involves choosing to calibrate or not and whether to make a new file
        if not self.apparatus.getValue(['information', 'materials', material, 'calibrated']):
            message = 'Would you like to use ink calibraton for ' + material + '?'
            options = ['y', 'n']
            default = 'y'
            self.useroptions.Do({'message': message, 'options': options, 'default': default})
            usecal = self.useroptions.response
            if usecal in ['Y', 'y', 'yes', 'Yes', '']:
                self.apparatus.setValue(['information', 'materials', material, 'calibrated'], True)
                message = 'Would you like to make a new file for ' + material + '?'
                options = ['y', 'n']
                default = 'n'
                self.useroptions.Do({'message': message, 'options': options, 'default': default})
                newfile = self.useroptions.response
                if newfile in ['Y', 'y', 'yes', 'Yes']:
                    # Clear existing file
                    cfilename = material + filename
                    tempfile = open(cfilename, mode='w')
                    json.dump([], tempfile)
                    tempfile.close()
                    self.cal_measurement.Do({'material': material})
                else:
                    message = 'Would you like to make new measurement of ' + material + '?'
                    options = ['y', 'n']
                    default = 'n'
                    self.useroptions.Do({'message': message, 'options': options, 'default': default})
                    newdata = self.useroptions.response
                    if newdata in ['Y', 'y', 'yes', 'Yes']:
                        self.cal_measurement.Do({'material': material})
                    else:
                        self.cal_calculation.Do({'material': material})

        else:
            self.cal_measurement.Do({'material': material})
