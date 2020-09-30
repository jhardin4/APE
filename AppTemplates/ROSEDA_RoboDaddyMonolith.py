def ROSEDA_RoboDaddyMonolith(apparatus, materials, tools, prime=None):
    # Creating all the initial device entries
    # Representative of local computer
    apparatus.add_device_entry('system', 'System')
    # Representative of the user
    apparatus.add_device_entry('user', 'User_Consol')
    # Create entry for gantry
    details = {
        'descriptors': ['motion'],
        'axes': ['X', 'Y', 'A', 'B', 'C', 'D'],
    }
    apparatus.add_device_entry('gantry', 'Aerotech_A3200_RoboDaddy', details)
    # Create a nozzle, nozzle slide, and pump for each material
    # Assumes that the prime nozzle is going to be using the Aerotech for
    # faster on/off
    n = 0  # Counter for keeping track of number of pumps
    for materialx in materials:
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
            'pressure': 0,
            'vacuum': 0,
            'COM': '',
        }
        apparatus.add_device_entry(f'pump{n}', 'Nordson_UltimusV', details)

        n += 1
    # Create entries for tools
    for tool in tools:
        details = {}
        # Gather important information for each kind of tool
        if tool['type'] == 'Panasonic_HGS_A3200':
            # Default Settings
            details['A3200name'] = 'gantry'
            details['systemname'] = 'system'
            details['retract'] = True
            details['axis'] = tool['axis']
            details['DOaxis'] = 'X'
            details['DObit'] = 0
            details['DIaxis'] = 'X'
            details['DIbit'] = 1

        if tool['type'] == 'IDS_ueye':
            details['settle_time'] = 5

        apparatus.add_device_entry(tool['name'], tool['type'], details)

    # Setting up interactions between tools/nozzles and gantry
    apparatus['information']['alignments'] = {}
    apparatus['information']['alignmentnames'] = ['initial']
    apparatus['information']['alignmentsfile'] = 'robodaddy_alignments.json'
    gantry = apparatus['devices']['gantry']
    alignments = apparatus['information']['alignments']
    alignment_names = apparatus['information']['alignmentnames']
    # Set default motion behavior for gantry
    gantry['default'] = {
        'speed': 40,
        'length_units': 'mm',
        'MotionRamp': 1000,
        'MaxAccel': 1000,
        'RelAbs': 'Abs',
        'LookAhead': True,
        'mode': 'loadrun',
        'axismask': {},
    }
    alignments['initial'] = {
        'X': '',
        'Y': '',
        'A': '',
        'B': '',
        'C': '',
        'D': '',
    }
    # Handle motion of each nozzle
    # Defaults to first material being the prime nozzle if another options is
    # not given
    if not prime:
        prime = True
        
    for materialx in materials:
        material = list(materialx)[0]
        zaxis = materialx[material]
        # motion details for nozzles
        gantry['n' + material] = {
            'speed': gantry['default']['speed'],
            'MotionRamp': gantry['default']['MotionRamp'],
            'MaxAccel': gantry['default']['MaxAccel'],
            'axismask': {'Z': zaxis},
        }
        gantry['n' + material + 'slide'] = {
            'speed': gantry['default']['speed'],
            'MotionRamp': gantry['default']['MotionRamp'],
            'MaxAccel': gantry['default']['MaxAccel'],
            'axismask': {'Z': zaxis},
        }
        # information location for each material

        alignment_names.append('n' + material + '@mark')
        alignments['n' + material + '@mark'] = {'X': '', 'Y': '', zaxis: ''}
        # treat first nozzle as prime nozzles
        if prime in [True, 'n' + material]:
            # Handle the start location
            alignment_names.append('n' + material + '@start')
            alignments['n' + material + '@start'] = {
                'X': '',
                'Y': '',
                zaxis: '',
            }
            # Handle the calibration location
            alignment_names.append('n' + material + '@cal')
            alignments['n' + material + '@cal'] = {
                'X': '',
                'Y': '',
                zaxis: '',
            }
            # Handle the clean location
            alignment_names.append('n' + material + '@clean')
            alignments['n' + material + '@clean'] = {
                'X': '',
                'Y': '',
                zaxis: '',
            }
            prime = False

    # Handle motion for each of the tools  
    for tool in tools:
        if tool['type'] == 'Panasonic_HGS_A3200':
            # Alignment information
            gantry[tool['name']] = {
                'speed': 40,
                'axismask': {'Z': tool['axis']},
            }
            alignment_names.append(tool['name'] + '@mark')
            alignments[tool['name'] + '@mark'] = {
                'X': '',
                'Y': '',
                tool['axis']: '',
            }
            alignments[tool['name'] + '@TP_init'] = {
                'X': -200,
                'Y': -250,
                tool['axis']: -50,
            }

        if tool['type'] == 'IDS_ueye':

            # Alignment information
            gantry['camera'] = {'speed': 40, 'axismask': {'Z': tool['axis']}}
            alignment_names.append(tool['name'] + '@mark')
            alignments[tool['name'] + '@mark'] = {
                'X': '',
                'Y': '',
                tool['axis']: '',
            }
        if prime == tool['name']:
            # Handle the start location
            alignment_names.append(tool['name'] + '@start')
            alignments[tool['name'] + '@start'] = {
                'X': '',
                'Y': '',
                tool['axis']: '',
            }
            # Handle the calibration location
            alignment_names.append(tool['name'] + '@cal')
            alignments[tool['name'] + '@cal'] = {
                'X': '',
                'Y': '',
                tool['axis']: '',
            }
            # Handle the clean location
            alignment_names.append(tool['name'] + '@clean')
            alignments[tool['name'] + '@clean'] = {
                'X': '',
                'Y': '',
                tool['axis']: '',
            }
            prime = False
    apparatus['information']['materials'] = {}
    apparatus['information']['calibrationfile'] = 'cal.json'
    apparatus['information']['ink calibration'] = {}
    apparatus['information']['ink calibration']['time'] = 60

    apparatus['information']['materials'][material] = {}
