from Core import Procedure
import json
import time


class Data_JSON_Store(Procedure):
    def Prepare(self):
        self.name = 'Data_JSON_Store'
        self.requirements['filename'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'motion to start',
        }
        self.requirements['value'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'value',
        }
        self.requirements['label'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'label of data',
        }
        self.requirements['newentry'] = {
            'source': 'apparatus',
            'address': '',
            'value': True,
            'desc': 'new ene',
        }

    def Plan(self):
        # Retreiving necessary device names

        # Getting necessary eprocs

        # Assign apparatus addresses to procedures

        # Doing stuff
        try:
            with open(self.filename, 'r') as TPjson:
                fdata = json.load(TPjson)
        except FileNotFoundError:
            fdata = []
            with open(self.filename, 'w') as TPjson:
                json.dump(fdata, TPjson)
        values = []
        if self.newentry:
            values.append(self.value)
            stime = time.time()
            newdataline = {'time': stime, self.label: values}
        else:
            newdataline = fdata.pop()
            newdataline[self.label].append(self.value)

        fdata.append(newdataline)

        with open(self.filename, 'w') as TPjson:
            json.dump(fdata, TPjson)
        self.apparatus.AddTicketItem({'data_file':self.filename})
