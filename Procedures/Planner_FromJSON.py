from Core import Procedure
import json

class Planner_FromJSON(Procedure):
    def Prepare(self):
        self.name = 'Planner_FromJSON'
        self.requirements['Apparatus_Addresses'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'path to store image'
            }
        self.requirements['file'] = {
            'source': 'apparatus',
            'address': ['information', 'planner_file'],
            'value': '',
            'desc': 'location to store plan'
            }
        self.counter = 0
        self.runlist = []
        self.allDone = False
        # Setup Apparatus
        if 'planner' not in self.apparatus['information']:
            self.apparatus['information']['planner'] = {}

    def Plan(self):
        # Renaming useful pieces of information
        addresses = self.requirements['Apparatus_Addresses']['value']
        file = self.requirements['file']['value']
        # Retreiving necessary device names

        # Retrieving information from apparatus

        # Getting necessary eprocs

        # Assign apparatus addresses to procedures

        # Doing stuff
        # Importing list of parameters from file
        
        with open(file, mode='r') as exp_design:
            self.runlist = json.load(exp_design)
        # Find the first new sample
        while self.runlist[self.counter]['done']:
            self.counter += 1
        # For each call, update the relevant values in the apparatus
        for dimension in self.runlist[self.counter]:
            #if dimension != 'done':
            if dimension not in ['done', 'Index', 'yGap', 'bzpoint2']:
                self.apparatus.setValue(addresses[dimension], self.runlist[self.counter][dimension])

    def sampleDone(self):
        self.runlist[self.counter]['done'] = True
        self.counter += 1
        file = self.requirements['file']['value']
        with open(file, mode='w') as exp_design:
            json.dump(self.runlist, exp_design) #THIS LINE IS WRONG... IT JUST APPENDS INSTEAD OF OVERWRITES
        exp_design.close()
        if self.counter >= len(self.runlist):
            self.allDone = True

