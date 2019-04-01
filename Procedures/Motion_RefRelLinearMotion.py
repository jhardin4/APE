from Core import Procedure

class Motion_RefRelLinearMotion(Procedure):
    def Prepare(self):
        self.name = 'Motion_RefRelLinearMotion'
        self.requirements['relpoint']={'source':'apparatus', 'address':'', 'value':'', 'desc':'Reference point'}
        self.requirements['refpoint']={'source':'apparatus', 'address':'','value':'', 'desc':'Point relative to reference position'}
        self.requirements['axismask']={'source':'apparatus', 'address':'','value':'', 'desc':'Dictionary of motion settings'}
        self.requirements['speed']={'source':'apparatus', 'address':'','value':'', 'desc':'order of operations for moving to a point'}

    def Plan(self):
        refpoint = self.requirements['refpoint']['value']
        relpoint = self.requirements['relpoint']['value']
        speed = self.requirements['speed']['value']
        axismask = self.requirements['axismask']['value']
        
        motionname = self.apparatus.findDevice({'descriptors':'motion'})
        
        move = self.apparatus.GetEproc(motionname, 'Move')

        
        
        #Assumes that reference points are in machine coordinates
        #Assumes that relative points are in tooltpath coordinates
        #Corrects the relative points to also be in machine coordinates
        #axismask is the mapping of toolpath coordinates to machine coordinates
        
        if axismask != '':
            for dim in axismask:
                if dim in relpoint:
                    relpoint[axismask[dim]]=relpoint[dim]
                    relpoint.pop(dim, None)          
        
        #Reference point sets which axes are used
        realpoint = {}
        for dim in refpoint:
            if dim in relpoint:
                realpoint[dim]=refpoint[dim]+relpoint[dim]
            else:
                realpoint[dim]=refpoint[dim]
            
        move.Do({'point':realpoint, 'speed':speed})
