from Core import Procedure
import time
from copy import deepcopy
import Procedures.Data_JSON_Store

class Planner_Combinatorial(Procedure):
    def Prepare(self):
        self.name = 'Planner_Combinatorial'
        self.requirements['space'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'ranges of each dimension'}
        self.requirements['Apparatus_Addresses'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'path to store image'}
        self.requirements['file'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'location to store plan'}
        self.requirements['priority'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'priority of dimensions'}
        self.logfile = Procedures.Data_JSON_Store(self.apparatus, self.executor)
        self.counter = 0
        self.firstrun = True
        self.runlist = []
        # Setup Apparatus
        if 'planner' not in self.apparatus['information']:
            self.apparatus['information']['planner'] = {}

    def Plan(self):
        # Renaming useful pieces of information
        space = self.requirements['space']['value']
        addresses = self.requirements['Apparatus_Addresses']['value']
        file = self.requirements['file']['value']
        priority = self.requirements['priority']['value']
        cpriority = priority.copy()
        # Retreiving necessary device names

        # Retrieving information from apparatus

        # Getting necessary eprocs

        # Assign apparatus addresses to procedures

        # Doing stuff
        # Construct the list of parameter sets to use if this is the first run
        space_index = []
        space_limit = []
        if self.firstrun:
            for dimension in priority:
                space_index.append(0)
                space_limit.append(len(space[dimension]))
            for n in range(len(priority)):
                dimension = cpriority.pop()
                # Check if runlist is empty
                if self.runlist == []:
                    for p in range(len(space[dimension])):
                        newline = {dimension: space[dimension][p]}
                        self.runlist.append(newline)
                else:
                    oldlength = len(self.runlist)
                    for l in range(len(self.runlist)):
                        for p in range(len(space[dimension])):
                                newline = deepcopy(self.runlist[l])
                                newline[dimension] = space[dimension][p]
                                self.runlist.append(newline)
                    self.runlist = self.runlist[oldlength:]

            self.firstrun = False
        # For each call, update the relevant values in the apparatus
        for dimension in self.runlist[self.counter]:
            self.apparatus.setValue(addresses[dimension], self.runlist[self.counter][dimension])
        self.logfile.Do({'filename': file, 'label': 'settings', 'value': self.runlist[self.counter], 'newentry': True})
        self.counter += 1