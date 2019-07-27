from Core import Procedure


class EndofLayer(Procedure):
    def Prepare(self):
        self.name = 'EndofLayer'
        self.requirements['layernumber'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'number of the layer',
        }
        # self.calink = Procedures.User_InkCal_Calibrate(self.apparatus, self.executor)

    def Plan(self):
        # Renaming useful pieces of informaiton
        _ = list(self.apparatus.getValue(['information', 'materials']))
        _ = self.requirements['layernumber']['value']
