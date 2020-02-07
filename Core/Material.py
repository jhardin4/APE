import uuid
import json
import copy

class MatError_Unit(Exception):
    def __init__(self, arg):
        self.arg = arg

units = []
mass_units = ['g', 'kg', 'lbs', 'oz']
length_units = ['m', 'cm', 'mm', 'in', 'um']
pressure_units = ['kPa', 'psi', 'atm']
vol_units = ['cc', 'mL', 'L']
density_units = []
for munit in mass_units:
    for vunit in vol_units:
        density_units.append(f'{munit}/{vunit}')

units = [
    None, 
    *mass_units,
    *length_units,
    *pressure_units,
    *vol_units,
    *density_units,
    ]


class material(dict):
    def __init__(self, file=None):
        dict.__init__(self)
        # Unique identifier for a specific material
        self['uuid'] = str(uuid.uuid4())
        # A list of all the names that this material is known by
        self['names'] = []
        # A list of all the other terms that might be used to describe
        # the material or its function.
        self['descriptors'] = []
        self['properties'] = {}
        self['components'] = {}
        self['recipe'] = ''
        self['manufacturer'] = ''
        self.units = units
        if file != None:
            self.load(file)

    def components(self):
        # Returns a dictionary of the components
        pass

    def add_property(self, name, value, unit):
        # Add properties to the material or update properties that already
        # exist.
        
        # Check that an appropriate unit is given
        if unit not in self.units:
            # Check to see if the unit needs to be added to the acceptable
            # list.
            print(f'{unit} was not found in acceptable unit list.')
            print('material.units contains the list of acceptable units.')
            response = input('Would you like to add {unit} to it? ([y],n)')
            # Update the units list if told to, otherwise, raise exception
            if response in ['', 'y']:
                self.units.append(unit)
            else:
                raise MatError_Unit(str(unit))
        # Update the property
        self['properties'][name] = {'value': value, 'unit': unit}
                
    def add_comp(self, lmaterial, vol_perc=None, mass_perc=None, use_name=None):
        # if no use_name is given, then use the first of its names
        if use_name == None:
            uname = lmaterial['names'][0]
        else:
            uname = use_name
        # Find a unique use_name for the component
        n = 0
        uname_found = False
        while not uname_found:
            if f'{uname}_{n}' in self['components']:
                n += 1
            else:
                uname_found = True
        uname += f'_{n}' 
        # Update the values
        self['components'][uname] = {
            'material': lmaterial,
            'vol_perc': vol_perc,
            'mass_perc': mass_perc,
            }

    def add_recipe(self, filename):
        file = open(filename)
        recipestring = file.read()
        self['recipe'] = recipestring
        
    def save(self, filename):
        # Prepare all of the relevant information for JSON serialization        
        self._addunits(self)
        with open(filename, mode='w') as file:
            json.dump(self, file)
        self._remunits(self)
    
    def _addunits(self, lmaterial):
        lmaterial['units'] = copy.deepcopy(lmaterial.units)
        for mat in lmaterial['components']:
            self._addunits(lmaterial['components'][mat]['material'])        
        
    def _remunits(self, lmaterial):
        if 'units' in lmaterial:
            del lmaterial['units']
        for mat in lmaterial['components']:
            self._remunits(lmaterial['components'][mat]['material'])
    
    def _prepare4JSON(self, material):
        pass

    def _rebuild4JSON(self, lmaterial, data):
        # Prepare all of the relevant information for JSON serialization
        # Go through all the materials in the components
        if lmaterial != self:
            newmat = material()
        else:
            newmat = self
        for key in data:
            newmat[key] = data[key]
        lmaterial = newmat
        for mat in lmaterial['components']:
            self._rebuild4JSON(lmaterial['components'][mat]['material'], data['components'][mat]['material'])

    def load(self, filename):
        # Loads a material from a file

        # Retreive data from file
        with open(filename, mode='r') as file:
            fmat = json.load(file)
        self._rebuild4JSON(self, fmat)
        self._remunits(self)
        # Walk through all the components, rebuilding them as materials
        
    def add_comp_file(self, filename, vol_perc=None, mass_perc=None, use_name=None):
        # Retreive data from file
        newmat = material()
        newmat.load(filename)
        self.add_comp(newmat, vol_perc, mass_perc, use_name)
    def push_cloud(self):
        # Place holder for this having the ability to connect with cloud repo
        # of materials
        pass
    def pull_cloud(self):
        # Place holder for this having the ability to connect with cloud repo
        # of materials
        pass
      
    
if __name__ == '__main__':
    fumed_silica = material()
    fumed_silica['names'].append('fumed silica')
    fumed_silica['names'].append('silica nanoparticles')
    fumed_silica.add_property('density', 1.0, 'g/cc')
    fumed_silica.save('fumed_silica.json')
    
    PDMS = material()
    PDMS['names'].append('PDMS')
    PDMS.add_property('density', 1.0, 'g/cc')
    
    silicone_oil = material()
    silicone_oil['names'].append('silicone oil')
    silicone_oil.add_property('density', 1.0, 'g/cc')
    
    
    
    PDMS.add_comp(silicone_oil, vol_perc=85)
    PDMS.add_comp_file('fumed_silica.json', vol_perc=10)
    PDMS.save('PDMS.json')
    # fumed_silica.load('fumed_silica.json')
    
    
        