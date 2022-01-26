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
            'value': [
                'information',
                'ProcedureData',
                'Toolpath_Generate',
                'toolpath',
            ],
            'address': '',
            'desc': 'where to store the toolpath',
        }
        self.requirements['dataArgs'] = {
            'source': 'apparatus',
            'address': ['information', 'ProcedureData', 'Toolpath_Generate', 'dataArgs'],
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
        self.apparatus.createAppEntry(
            ['information', 'ProcedureData', 'Toolpath_Generate', 'dataArgs']
        )
        # This creates an dummy entry for 
        self.material_name_add = [
                'information',
                'ProcedureData',
                'Toolpath_Generate',
                'parameters',
                'materialname',
                ]
        self.material = None

    def Plan(self):
        # Set up the parameters for the toolpath generator
        self.setParameters()
        # Run the toolpath generator
        systemname = self.apparatus.findDevice(descriptors='system')
        temptarget = [0]
        self.DoEproc(
            systemname,
            'Run',
            {
                'address': self.generator + '.GenerateToolpath',
                'addresstype': 'pointer',
                'arguments': [self.parameters, temptarget],
            },
        )
        self.apparatus.setValue(self.target, temptarget)
        self.printTP.requirements['target']['address'] = self.target
        self.printTP.Do({'newfigure': True})

    def setMaterial(self, material, mat_add=''):
        # this assumes your are working with a "primary" toolpath generator
        self.material = material
        if type(mat_add) == list:
            self.apparatus.createAppEntry(mat_add)
            self.apparatus.setValue(mat_add, material)

    def setGenerator(self, generator):
        self.apparatus.setValue(
                self.requirements['generator']['address'], generator
                )

    def setParameters(self):
        # Update values to ensure the right ones are used
        self.GetRequirements({})
        # Assume that at least a material name is needed.
        if self.dataArgs in ['', None, [], {}]:
            if not self.material:
                self.material = self.apparatus.getValue(
                    self.material_name_add
                )
            self.dataArgs = [self.material]
            self.requirements["dataArgs"]["value"] = [self.material]

        # Import the specific toolpath generation file and make a parameters
        # entry using the parameter generator in that file
        TPGen = import_module(self.generator)
        reload(TPGen)
        tempPara = TPGen.Make_TPGen_Data(*self.dataArgs)

        # Update the procedure values
        self.parameters = tempPara
        self.requirements["parameters"]["value"] = tempPara
        para_address = self.requirements["parameters"]["address"]
        # Update the apparatus if an address is listed
        if type(para_address) == list:
            self.apparatus.setValue(para_address, tempPara)
