from Core import Procedure
import Parses
import Procedures.Motion_RefRelLinearMotion

        
class Toolpath_Print(Procedure):
    def Prepare(self):
        self.name = 'Toolpath_Print'
        self.requirements['toolpath'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'toolpath to be printed'}
        self.move = Procedures.Motion_RefRelLinearMotion(self.apparatus, self.executor)
        self.start = Parses.Start(self.apparatus, self.executor)
        self.startmotion = Parses.StartofMotion(self.apparatus, self.executor)
        self.endmotion = Parses.EndofMotion(self.apparatus, self.executor)
        self.changemat = Parses.ChangeMat(self.apparatus, self.executor)
        self.endoflayer = Parses.EndofLayer(self.apparatus, self.executor)
        self.end = Parses.End(self.apparatus, self.executor)

          
    
    def Plan(self):
        #Renaming useful pieces of informaiton
        toolpath = self.requirements['toolpath']['value'][0]

        #Retreiving necessary device names
        
        #Getting necessary eprocs
        
        #Assign apparatus addresses to procedures
        
        #Doing stuff
        for line in toolpath:
            if 'parse' in line:
                if line['parse']=='start':
                    self.start.Do()
                if line['parse']=='startofmotion':
                    self.startmotion.Do({'motion':line['motion']})
                if line['parse']=='endofmotion':
                    self.endmotion.Do({'motion':line['motion']})
                if line['parse']=='changemat':
                    self.changemat.Do({'startmotion':line['startmotion'],'endmotion':line['endmotion']})
                if line['parse']=='endoflayer':
                    self.endoflayer.Do({'layernumber':line['number']})
                if line['parse']=='end':
                    self.end.Do()
            else:
                motionname = self.apparatus.findDevice({'descriptors': 'motion' })
                nozzlename = self.apparatus.findDevice({'descriptors':['nozzle', line['material']] })
                refpoint = self.apparatus['information']['alignments'][nozzlename+'@start']
                speed = self.apparatus['devices'][motionname][nozzlename]['speed']
                axismask = self.apparatus['devices'][motionname][nozzlename]['axismask']
                self.move.Do({'refpoint':refpoint,'relpoint':line['endpoint'], 'speed':speed, 'axismask':axismask})
