from Core import Procedure
from Procedures import Toolpath_Generate, Toolpath_Print, Planner_Combinatorial


class PrintSample(Procedure):
    def Prepare(self):
        self.name = 'PrintSample'
        self.requirements['samplename'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'name of this sample for logging purposes',
        }
        self.gentp = Toolpath_Generate(self.apparatus, self.executor)
        self.printtp = Toolpath_Print(self.apparatus, self.executor)
        self.planner = Planner_Combinatorial(self.apparatus, self.executor)

    def Plan(self):
        # Renaming useful pieces of informaiton
        _ = self.requirements['samplename']['value']

        '''
        # Set the plan space from tip height and anticipated trace height
        space = {'tiph': [0.01*n for n in range(8)]}
        space['trace_height'] = [0.1 * n for n in range(1, 6)]
        # Set the Apparatus addresses for tip heigh ant anticipate trace height
        addresses = {'tiph': ['information', 'toolpaths', 'parameters', 'tiph']}
        addresses['trace_height'] = ['devices', 'nAgPMMA', 'trace_height']
        # Set the priority of exploration
        priority = ['tiph', 'trace_height']
        # Set where to store the planner log
        file = 'Data//planner.json'
        self.planner.Do({'space': space, 'Apparatus_Addresses': addresses, 'file': file, 'priority': priority})
        '''
        # Generate Toolpath
        self.gentp.Do()
        self.printtp.Do({'toolpath': self.gentp.requirements['target']['value']})

        # if self.apparatus.simulation:
        #    time.sleep(1)  # Just in for demonstration
