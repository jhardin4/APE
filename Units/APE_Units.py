import json

class InvalidApparatusAddressException(Exception):
    pass

class APE_units():
    def __init__(self, ufile=None):
        if ufile == None:
            self.unitmap = {}
        else:
            self.load_units(ufile)

    def set_units(self, app_address, unit):
        level = self.unitmap
        lastlevel = app_address[-1]
        current_address = []
        for branch in app_address[:-1]:
            current_address.append(branch)
            try:
                level = level[branch]
            except TypeError:
                raise InvalidApparatusAddressException(
                    f'Type does not match: {app_address}'
                )
            except KeyError:
                self._create_entry(app_address)
                level = level[branch]

        level[lastlevel]['unit'] = unit
        
    def _create_entry(self, app_address):
        target = self.unitmap
        # Build everything but the last entry
        for entry in app_address[:-1]:
            if entry in target:
                if type(target[entry]) == dict:
                    target = target[entry]
                else:
                    raise Exception(
                        str(entry) + ' in ' + str(app_address) + ' is already occupied'
                    )
            else:
                target[entry] = {}
                target = target[entry]
        if app_address[-1] not in target:
            target[app_address[-1]] = {}
            
    def convert_units(self, app_address, unit):
        pass

    def get_units(self, app_address):
        level = self.unitmap
        unit_list = ['']
        for branch in app_address:
            if type(level) == dict and branch in level:
                if 'unit' in level[branch]:
                    unit_list.append(level[branch]['unit'])
                level = level[branch]
        print(unit_list)
        return unit_list.pop()

    def save_units(self, filename):
        with open(filename, mode='w') as udata:
            json.dump(self.unitmap, udata)

    def load_units(self, filename):
        with open(filename) as udata:
            self.unitmap = json.load(udata)
            
if __name__ == '__main__':
    units = APE_units()
    unit1_address = ['devices', 'gantry', 'speed']
    units.set_units(unit1_address, 'mm/s')
    unit2_address = ['information', 'alignments']
    units.set_units(unit2_address, 'mm')
    unit3_address = ['devices', 'gantry']
    units.set_units(unit3_address, 'mm')
    unit4_address = ['information', 'alignments', 'nozzle']
    
    print(units.get_units(unit1_address))
    print(units.get_units(unit4_address))
    
    units.save_units('unit_file.json')
    units.load_units('unit_file.json')