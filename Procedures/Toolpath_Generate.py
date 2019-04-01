from Core import Procedure
import Procedures.Toolpath_Plot


class Toolpath_Generate(Procedure):
    def Prepare(self):
        self.name = 'Toolpath_Generate'
        self.requirements['parameters']={'source':'apparatus', 'address':'', 'value':'', 'desc':'parameters used to generate toolpath'}
        self.requirements['generator']={'source':'apparatus', 'address':'', 'value':'', 'desc':'pointer to generator'}
        self.requirements['target']={'source':'apparatus', 'address':'', 'value':'', 'desc':'where to store the toolpath'}
        self.requirements['parameters']['address']=['information','toolpaths','parameters']
        self.requirements['generator']['address']=['information','toolpaths','generator']
        self.requirements['target']['address']=['information','toolpaths','toolpath']
        self.printTP = Procedures.Toolpath_Plot(self.apparatus, self.executor)
    
    def Plan(self):
        parameters = self.requirements['parameters']['value']
        generator = self.requirements['generator']['value']
        target = self.requirements['target']['value']        
        
        systemname = self.apparatus.findDevice({'descriptors':'system'})
        
        runprog = self.apparatus.GetEproc(systemname, 'Run')
        
        runprog.Do({'address':generator, 'addresstype':'pointer', 'arguments':[parameters, target]})
        self.printTP.Do({'newfigure': True})
