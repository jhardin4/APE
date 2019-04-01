from Core import Procedure


class Aerotech_A3200_Set(Procedure):
    def Prepare(self):
        self.name = 'Aerotech_A3200_Set'
        self.requirements['Type']={'source':'apparatus', 'address':'', 'value':'', 'desc':'name of the full description of A3200 movement stored under the motion devices in the apparatus'}

    def Plan(self):
        motionname = self.apparatus.findDevice({'descriptors': 'motion'})
        setmotion = self.apparatus.GetEproc(motionname, 'Set_Motion')
        settinglist = {}
        if not self.requirements['Type']['value'] in self.apparatus['devices'][motionname]:
            raise Exception(str(self.requirements['Type']['value']) + ' not found under ' + motionname)
        for req in setmotion.requirements:
            if req in self.apparatus['devices'][motionname][self.requirements['Type']['value']]:
                settinglist[req]=self.apparatus['devices'][motionname][self.requirements['Type']['value']][req]
            
        setmotion.Do(settinglist)

