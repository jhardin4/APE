from Core import Procedure
import Procedures.Toolpath_Plot
from importlib import import_module, reload


class Toolpath_Generate(Procedure):
    def Prepare(self):
        self.name = 'Toolpath_Generate'
        self.requirements['parameters'] = {
            'source': 'apparatus',
            'address': ['information', 'ProcedureData', 'Toolpath_Generate', 'parameters'],
            'value': '',
            'desc': 'parameters used to generate toolpath',
        }
        self.requirements['generator'] = {
            'source': 'apparatus',
            'address': ['information', 'ProcedureData', 'Toolpath_Generate', 'generator'],
            'value': '',
            'desc': 'name of generator',
        }
        self.requirements['target'] = {
            'source': 'apparatus',
            'address': ['information', 'ProcedureData', 'Toolpath_Generate', 'toolpath'],
            'value': '',
            'desc': 'where to store the toolpath',
        }
        self.requirements['dataArgs'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'arguments to make parameter structure',
        }
        self.printTP = Procedures.Toolpath_Plot(self.apparatus, self.executor)
        self.apparatus.createAppEntry(
            ['information', 'ProcedureData', 'Toolpath_Generate', 'toolpath']
        )
        self.printTP = Procedures.Toolpath_Plot(self.apparatus, self.executor)
        self.apparatus.createAppEntry(
            ['information', 'ProcedureData', 'Toolpath_Generate', 'parameters']
        )
        self.printTP = Procedures.Toolpath_Plot(self.apparatus, self.executor)
        self.apparatus.createAppEntry(
            ['information', 'ProcedureData', 'Toolpath_Generate', 'generator']
        )

    def Plan(self):
        parameters = self.requirements['parameters']['value']
        generator = self.requirements['generator']['value']
        target = self.requirements['target']['value']
        dataArgs = self.requirements['dataArgs']['value']

        # If no arguments for the generator are given, use the material name
        # from the default parameters location
        if dataArgs == '':
            material = self.apparatus.getValue(
                ['information', 'ProcedureData', 'Toolpath_Generate', 'parameters', 'materialname']
            )
            dataArgs = [material]

        # Import the specific toolpath generation file and make a parameters
        # entry using the parameter generator in that file
        TPGen = import_module(generator)
        reload(TPGen)
        tempPara = TPGen.Make_TPGen_Data(*dataArgs)

        # Determine if a new set of parameters needs to be created
        # This typically has to be done for the first run of the generator
        newPara = False
        if type(parameters) != dict:
            newPara = True
        else:
            for key in tempPara:
                if key not in parameters:
                    newPara = True
        if newPara:
            parameters = tempPara
            self.apparatus.setValue(
                ['information', 'ProcedureData', 'Toolpath_Generate', 'parameters'], tempPara
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
