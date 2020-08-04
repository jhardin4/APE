from Core import Procedure
import Procedures.Toolpath_Generate
import Procedures.User_InkCal_Measure


class ROSEDA_TestMaterial(Procedure):
    def Prepare(self):
        self.name = 'ROSEDA_TestMaterial'
        self.GenTP = Procedures.Toolpath_Generate(self.apparatus, self.executor)
        self.PrintTP = Procedures.Toolpath_Print(self.apparatus, self.executor)
        self.Planner = Procedures.Planner_Combinatorial(self.apparatus, self.executor)
        self.move = Procedures.Motion_RefRelLinearMotion(self.apparatus, self.executor)
        self.pmove = Procedures.Motion_RefRelPriorityLineMotion(self.apparatus, self.executor)
        self.requirements['material'] = {
            'source': 'direct',
            'address': '',
            'value': '',
            'desc': 'material to be used',
        }
        self.requirements['parameters'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'material to be used',
        }
        
    def Plan(self):
        # Setting up a toolpath generator indepenent of the 
        # "main" one.
        self.GenTP.setMaterial(self.material)
        self.GenTP.requirements['generator']['source'] = 'direct'
        self.GenTP.requirements['generator']['value'] = 'Ros3daTPGen'
        # parameters and dataArgs have to be explicitly set
        # to avoid using main TPGen data
        self.GenTP.setParameters(parameters=self.parameters, dataArgs=[self.material])  # Creates the parameter structure for TPGen
        # Set to toolpath address to be within this
        # procedures Apparatus data
        rosedaTP_address = ['information', 'ProcedureData', 'ROSEDA_TestMaterial', 'toolpath']
        self.GenTP.requirements['target']['address'] = rosedaTP_address
        self.apparatus.createAppEntry(rosedaTP_address)
        # Generate the toolpath for everything but the dots
        self.GenTP.Do()
        
        # Print the toolpath for the everything but the dots and crosses
        self.PrintTP.requirements['toolpath']['address'] = rosedaTP_address
        
        # Find all the relevant devices
        motionname = self.apparatus.findDevice(descriptors='motion')
        nozzlename = self.apparatus.findDevice(descriptors=['nozzle', self.material])
        pumpname = self.apparatus.findDevice(descriptors=['pump', self.material])
        
        # Set up move and pmove
        self.move.requirements['axismask']['address'] = ['devices', motionname, nozzlename, 'axismask']
        self.move.requirements['speed']['address'] = ['devices', motionname, nozzlename, 'speed']
        self.move.requirements['refpoint']['address'] = ['information', 'alignments', nozzlename + '@start']

        self.pmove.requirements['axismask']['address'] = ['devices', motionname, nozzlename, 'axismask']
        self.pmove.requirements['refpoint']['address'] = ['information', 'alignments', nozzlename + '@start']        

        pressure = self.apparatus.getValue(
            ['devices', pumpname, 'pressure']
        )

        self.DoEproc(pumpname, 'Set', {'pressure':pressure})
        self.printDotted([2.0,1.75,1.5,1.25,1.0,0.75,0.5], motionname, pumpname)
        self.printCrossing([1,5,25,100], motionname)        
    def printDotted(self, periods, motionname, pumpname):
        # Likely this is not the best way to command motion.
        for ind,period in enumerate(periods):
            self.pmove.Do(
                {
                    'relpoint': {'X':4, 'Y':5+4*(ind), 'Z':0.6},
                    'speed': 20,
                    'priority': [['X', 'Y'], ['Z']],
                }
            )
            self.DoEproc(motionname, 'Run', {})
            
            speed = self.apparatus.getValue(self.move.requirements['speed']['address'])
            time_to_complete = 20/speed

            for i in [x*period for x in range(0,int(time_to_complete/period),2)]:
                self.DoEproc(pumpname, 'DelayedOn', {'delay':i})
                self.DoEproc(pumpname, 'DelayedOff', {'delay':i+period})

            self.move.Do(
                {
                    'relpoint': {'X':24, 'Y':5+4*(ind), 'Z':0.6},
                }
            )
            self.DoEproc(motionname, 'Run', {})
            self.move.Do(
                {
                    'relpoint': {'X':24, 'Y':5+4*(ind), 'Z':0},
                }
            )
            self.DoEproc(motionname, 'Run', {})
            self.move.Do(
                {
                    'relpoint': {'X':24, 'Y':5+4*(ind), 'Z':10},
                }
            )
            self.DoEproc(motionname, 'Run', {})
        
    def printCrossing(self, cross_feeds, motionname):
        # Go to first crossing
        self.pmove.Do(
            {
                'relpoint': {'X':34-6, 'Y':39.4+8, 'Z':0.0},
                'speed': 20,
                'priority': [['X', 'Y'], ['Z']],
            }
        )
        self.DoEproc(motionname, 'Run', {})
        self.move.Do(
            {
                'relpoint': {'X':34-6, 'Y':39.4-8, 'Z':0.0},
                'speed': cross_feeds[0],
            }
        )
        self.DoEproc(motionname, 'Run', {})
        self.move.Do(
            {
                'relpoint': {'X':34-6, 'Y':39.4-8, 'Z':5},
            }
        )
        self.DoEproc(motionname, 'Run', {})

        # Got to 2nd crossing
        self.pmove.Do(
            {
                'relpoint': {'X':34-2*6, 'Y':39.4+8, 'Z':0.0},
                'speed': 20,
                'priority': [['X', 'Y'], ['Z']],
            }
        )
        self.DoEproc(motionname, 'Run', {})
        self.move.Do(
            {
                'relpoint': {'X':34-2*6, 'Y':39.4-8, 'Z':0.0},
                'speed': cross_feeds[1],
            }
        )
        self.DoEproc(motionname, 'Run', {})
        self.move.Do(
            {
                'relpoint': {'X':34-2*6, 'Y':39.4-8, 'Z':5},
            }
        )
        self.DoEproc(motionname, 'Run', {})
        
        # Go to third crossing
        self.pmove.Do(
            {
                'relpoint': {'X':34-3*6, 'Y':39.4+8, 'Z':0.0},
                'speed': 20,
                'priority': [['X', 'Y'], ['Z']],
            }
        )
        self.DoEproc(motionname, 'Run', {})
        self.move.Do(
            {
                'relpoint': {'X':34-3*6, 'Y':39.4-8, 'Z':0.0},
                'speed': cross_feeds[2],
            }
        )
        self.DoEproc(motionname, 'Run', {})
        self.move.Do(
            {
                'relpoint': {'X':34-3*6, 'Y':39.4-8, 'Z':5},
            }
        )
        self.DoEproc(motionname, 'Run', {})

        # Go to fourth crossing
        self.pmove.Do(
            {
                'relpoint': {'X':34-4*6, 'Y':39.4+8, 'Z':0.0},
                'speed': 20,
                'priority': [['X', 'Y'], ['Z']],
            }
        )
        self.DoEproc(motionname, 'Run', {})
        self.move.Do(
            {
                'relpoint': {'X':34-4*6, 'Y':39.4-8, 'Z':0.0},
                'speed': cross_feeds[3],
            }
        )
        self.DoEproc(motionname, 'Run', {})
        self.move.Do(
            {
                'relpoint': {'X':34-4*6, 'Y':39.4-8, 'Z':5},
            }
        )
        self.DoEproc(motionname, 'Run', {})


