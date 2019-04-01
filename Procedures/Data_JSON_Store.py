from Core import Procedure
import json
import time


class Data_JSON_Store(Procedure):
    def Prepare(self):
        self.name = 'Data_JSON_Store'
        self.requirements['filename'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'motion to start'}
        self.requirements['value'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'value'}
        self.requirements['label'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'label of data'}
        self.requirements['newentry'] = {'source': 'apparatus', 'address': '', 'value': True, 'desc': 'new ene'}

    def Plan(self):
        # Renaming useful pieces of informaiton
        filename = self.requirements['filename']['value']
        newentry = self.requirements['newentry']['value']
        label = self.requirements['label']['value']
        value = self.requirements['value']['value']

        # Retreiving necessary device names

        # Getting necessary eprocs

        # Assign apparatus addresses to procedures

        # Doing stuff
        try:
            with open(filename, 'r') as TPjson:
                fdata = json.load(TPjson)
        except FileNotFoundError:
            fdata = []
            with open(filename, 'w') as TPjson:
                json.dump(fdata, TPjson)
        values = []
        if newentry:
            values.append(value)
            stime = time.time()
            newdataline = {'time': stime, label: values}
        else:
            newdataline = fdata.pop()
            newdataline[label].append(value)

        fdata.append(newdataline)

        with open(filename, 'w') as TPjson:
            json.dump(fdata, TPjson)
