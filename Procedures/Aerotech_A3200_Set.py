from Core import Procedure


class Aerotech_A3200_Set(Procedure):
    def Prepare(self):
        self.name = 'Aerotech_A3200_Set'
        self.requirements['Type'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'name of the full description of A3200 movement stored under the motion devices in the apparatus',
        }

    def Plan(self):
        motionname = self.apparatus.findDevice(descriptors='motion')
        settinglist = {}
        settingTypes = self.apparatus.getValue(['devices', motionname])
        if self.Type not in settingTypes:
            raise Exception(str(self.Type) + ' not found under ' + motionname)
        setReqs = self.executor.devicelist[motionname]['Address'].getRequirements(
            'Set_Motion'
        )
        typeSettings = self.apparatus.getValue(['devices', motionname, self.Type])
        for req in setReqs:
            if req in typeSettings:
                settinglist[req] = self.apparatus.getValue(
                    ['devices', motionname, self.Type, req]
                )

        self.DoEproc(motionname, 'Set_Motion', settinglist)
