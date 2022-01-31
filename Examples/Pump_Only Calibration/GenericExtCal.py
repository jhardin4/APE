def ExtCal(apparatus, materials):
    apparatus.add_device_entry('user', 'User_Consol')
    apparatus.add_device_entry('system', 'System')
    apparatus['information']['materials'] = {}
    for n, materialx in enumerate(materials):
        material = list(materialx)[0]
        apparatus.add_device_entry(
            f'n{material}',
            details={'descriptors': ['nozzle', material]}
        )
        apparatus.add_device_entry(
            f'n{material}slide',
            details={'descriptors': ['nozzle', f'{material}slide']}
        )
        details = {
            'type': 'Pump',
            'pressure': 0,
            'vacuum': 0,
            'COM': '',
        }    
        apparatus.add_device_entry(f'extruder{n}', 'Pump', details)
        apparatus['information']['materials'][material] = {}
    apparatus.proclog = []
    apparatus['information']['calibrationfile'] = 'cal.json'
    apparatus['information']['ink calibration'] = {}
    apparatus['information']['ink calibration']['time'] = 60
    apparatus['proclog'] = apparatus.proclog

