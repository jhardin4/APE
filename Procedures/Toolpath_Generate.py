from Core import Procedure
import Procedures.Toolpath_Plot
from importlib import import_module, reload


class Toolpath_Generate(Procedure):
    def Prepare(self):
        self.name = 'Toolpath_Generate'
        self.requirements['parameters'] = {
            'source': 'apparatus',
            'address': [
                'information',
                'ProcedureData',
                'Toolpath_Generate',
                'parameters',
            ],
            'value': '',
            'desc': 'parameters used to generate toolpath',
        }
        self.requirements['generator'] = {
            'source': 'apparatus',
            'address': [
                'information',
                'ProcedureData',
                'Toolpath_Generate',
                'generator',
            ],
            'value': '',
            'desc': 'name of generator',
        }
        self.requirements['target'] = {
            'source': 'apparatus',
            'address': [
                'information',
                'ProcedureData',
                'Toolpath_Generate',
                'toolpath',
            ],
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
        # This creates an dummy entry for 
        self.material_name_add = [
                'information',
                'ProcedureData',
                'Toolpath_Generate',
                'parameters',
                'materialname',
                ]

    def Plan(self):
        parameters = self.requirements['parameters']['value']
        generator = self.requirements['generator']['value']
        target = self.requirements['target']['address']
        dataArgs = self.requirements['dataArgs']['value']

        # Set up the parameters for the toolpath generator
        self.setParameters(parameters=parameters, generator=generator, dataArgs=dataArgs)
        # Run the toolpath generator
        systemname = self.apparatus.findDevice(descriptors='system')
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
        self.apparatus.setValue(target, temptarget)
        self.printTP.requirements['target']['address'] = target
        self.printTP.Do({'newfigure': True})

    def setMaterial(self, material):
        self.apparatus.createAppEntry([
                'information',
                'ProcedureData',
                'Toolpath_Generate',
                'parameters',
                'materialname',
                ])
        self.apparatus.setValue(
                [
                    'information',
                    'ProcedureData',
                    'Toolpath_Generate',
                    'parameters',
                    'materialname',
                ],
                material)

    def setGenerator(self, generator):
        self.apparatus.setValue(
                self.requirements['generator']['address'], generator
                )

    def setParameters(self, parameters='', generator='', dataArgs=''):
        # Update values to ensure the right ones are used
        values = {}
        if parameters != '':
            values['parameters'] = parameters
        if generator != '':
            values['generator'] = generator
        if dataArgs != '':
            values['dataArgs'] = dataArgs
        self.GetRequirements(values)
        parameters = self.requirements['parameters']['value']
        generator = self.requirements['generator']['value']
        if dataArgs == '':
            material = self.apparatus.getValue(
                [
                    'information',
                    'ProcedureData',
                    'Toolpath_Generate',
                    'parameters',
                    'materialname',
                ]
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
                ['information', 'ProcedureData', 'Toolpath_Generate', 'parameters'],
                tempPara,
            )
