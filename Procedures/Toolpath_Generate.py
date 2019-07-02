from Core import Procedure
import Procedures.Toolpath_Plot
from importlib import import_module


class Toolpath_Generate(Procedure):
    def Prepare(self):
        self.name = 'Toolpath_Generate'
        self.requirements['parameters'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'parameters used to generate toolpath',
        }
        self.requirements['generator'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'name of generator',
        }
        self.requirements['target'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'where to store the toolpath',
        }
        self.requirements['dataArgs'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'arguments to make parameter structure',
        }
        self.requirements['parameters']['address'] = [
            'information',
            'toolpaths',
            'parameters',
        ]
        self.requirements['generator']['address'] = [
            'information',
            'toolpaths',
            'generator',
        ]
        self.requirements['target']['address'] = [
            'information',
            'toolpaths',
            'toolpath',
        ]
        self.printTP = Procedures.Toolpath_Plot(self.apparatus, self.executor)

    def Plan(self):
        parameters = self.requirements['parameters']['value']
        generator = self.requirements['generator']['value']
        target = self.requirements['target']['value']
        dataArgs = self.requirements['dataArgs']['value']

        if dataArgs == '':
            material = self.apparatus.getValue(
                ['information', 'toolpaths', 'parameters', 'materialname']
            )
            dataArgs = [material]

        TPGen = import_module(generator)
        tempPara = TPGen.Make_TPGen_Data(*dataArgs)
        newPara = False
        for key in tempPara:
            if key not in parameters:
                newPara = True
        if newPara:
            parameters = tempPara
            self.apparatus.setValue(
                ['information', 'toolpaths', 'parameters'], tempPara
            )

        systemname = self.apparatus.findDevice({'descriptors': 'system'})
        temptarget = [0]
        self.DoEproc(
            systemname,
            'Run',
            {
                'address': generator + '.GenerateToolpath',
                'addresstype': 'pointer',
                'arguments': [parameters, temptarget],
            },
        )
        self.apparatus.setValue(self.requirements['target']['address'], temptarget)
        self.printTP.Do({'newfigure': True})
