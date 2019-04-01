from Core import Procedure


class Motion_RefRelPriorityLineMotion(Procedure):
    def Prepare(self):
        self.name = 'Motion_RefRelPriorityLineMotion'
        self.requirements['relpoint']={'source':'apparatus', 'address':'', 'value':'', 'desc':'Reference point'}
        self.requirements['refpoint']={'source':'apparatus', 'address':'','value':'', 'desc':'Point relative to reference position'}
        self.requirements['speed']={'source':'apparatus', 'address':'','value':'', 'desc':'Target speed, typicalling in mm/s'}
        self.requirements['axismask']={'source':'apparatus', 'address':'','value':'', 'desc':'Dictionary of motion settings'}
        self.requirements['priority']={'source':'apparatus', 'address':'','value':'', 'desc':'order of operations for moving to a point'}

    def Plan(self):
        refpoint = self.requirements['refpoint']['value']
        relpoint = self.requirements['relpoint']['value']
        speed = self.requirements['speed']['value']
        axismask = self.requirements['axismask']['value']
        priority= self.requirements['priority']['value']
        
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
        
        #Since the priority is relative to toolpath coordinates as well, it also has to be corrected
        for line in priority:
            for n in range(len(line)):
                if line[n] in axismask:
                    old_dim = line[n]
                    line[n] = axismask[old_dim]
        
        #print(str(priority))
        
        #Go line by line in the priority and execute a refrel motion for each line
        for line in priority:
            realpoint = {}
            for pdim in line:
                if pdim in refpoint:
                    if pdim in relpoint:
                        realpoint[pdim]=refpoint[pdim]+relpoint[pdim]
                    else:
                        realpoint[pdim]=refpoint[pdim]
            
            move.Do({'point':realpoint, 'speed':speed})
