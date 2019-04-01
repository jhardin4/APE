from Core import Procedure


class User_FlexPrinter_Alignments_Derive(Procedure):
    def Prepare(self):
        self.name = 'User_FlexPrinter_Alignments_Derive'
        self.requirements['Measured_List']={'source':'apparatus', 'address':'', 'value':'', 'desc':'list of measurements'}
        self.requirements['primenoz']={'source':'apparatus', 'address':'', 'value':'', 'desc':'prime material'}
    
    def Plan(self):
        measuredlist = self.requirements['Measured_List']['value']
        primenoz = self.requirements['primenoz']['value']
        alignments = self.apparatus['information']['alignments']
        
        motionname = self.apparatus.findDevice({'descriptors':'motion'})
        
        toollist = [n.partition('@')[0] for n in measuredlist]
        
        #Doing stuff 
        alignments['safeZZ1'] = {'ZZ1':alignments['initial']['ZZ1']}
        alignments['safeZZ2'] = {'ZZ2':alignments['initial']['ZZ2']}
        alignments['safeZZ3'] = {'ZZ3':alignments['initial']['ZZ3']}
        alignments['safeZZ4'] = {'ZZ4':alignments['initial']['ZZ4']}
        
        toollist.remove('initial')
        
        paxismask = self.apparatus['devices'][motionname][primenoz]['axismask']
        pzaxis = 'Z'
        if 'Z' in paxismask:
            pzaxis =paxismask['Z']

        for tool in toollist:
            zaxis = 'Z'
            axismask = self.apparatus['devices'][motionname][tool]['axismask']
            if 'Z' in axismask:
                zaxis =axismask['Z']

            for name in [tool+'@start',tool+'slide@start',tool+'@cal']:
                if name not in alignments:
                    alignments[name]={}
            alignments[tool+'@start']['X']=alignments[primenoz+'@start']['X'] -(alignments[primenoz+'@mark']['X'] - alignments[tool+'@mark']['X'])
            alignments[tool+'@start']['Y']=alignments[primenoz+'@start']['Y'] -(alignments[primenoz+'@mark']['Y'] - alignments[tool+'@mark']['Y'])
            alignments[tool+'@start'][zaxis]=alignments[primenoz+'@start'][pzaxis] -(alignments[primenoz+'@mark'][pzaxis] - alignments[tool+'@mark'][zaxis])
            alignments[tool+'slide@start'] = alignments[tool+'@start']
            alignments[tool+'@cal']['X']=alignments[primenoz+'@cal']['X'] -(alignments[primenoz+'@mark']['X'] - alignments[tool+'@mark']['X'])
            alignments[tool+'@cal']['Y']=alignments[primenoz+'@cal']['Y'] -(alignments[primenoz+'@mark']['Y'] - alignments[tool+'@mark']['Y'])
            alignments[tool+'@cal'][zaxis]=alignments[primenoz+'@cal'][pzaxis] -(alignments[primenoz+'@mark'][pzaxis] - alignments[tool+'@mark'][zaxis])
