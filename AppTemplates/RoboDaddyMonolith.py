def RoboDaddyMonolith(apparatus, materials, tools):
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
        if tool['type'] == 'Keyence_GT2_A3200':
            # Default Settings
            details['A3200name'] = 'gantry'
            details['systemname'] = 'system'
            details['retract'] = True
            details['zreturn'] = 5
            details['axis'] = tool['axis']
            details['DOaxis'] = 'A'
            details['DObit'] = 0
            details['AIaxis'] = 'B'
            details['AIchannel'] = 0

        if tool['type'] == 'IDS_ueye_3250CP2':
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
    primenozzle = True
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
        if primenozzle:
            alignment_names.append('n' + material + '@start')
            alignments['n' + material + '@start'] = {
                'X': '',
                'Y': '',
                zaxis: '',
            }
            alignment_names.append('n' + material + '@cal')
            alignments['n' + material + '@cal'] = {
                'X': '',
                'Y': '',
                zaxis: '',
            }
            primenozzle = False

    # Handle motion for each of the tools
    for tool in tools:
        if tool['type'] == 'Keyence_GT2_A3200':
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
                'B': -50,
            }

        if tool['type'] == 'IDS_ueye_3250CP2':

            # Alignment information
            gantry['camera'] = {'speed': 40, 'axismask': {'Z': tool['axis']}}
            alignment_names.append(tool['name'] + '@mark')
            alignments[tool['name'] + '@mark'] = {
                'X': '',
                'Y': '',
                tool['axis']: '',
            }
    apparatus['information']['materials'] = {}
    apparatus['information']['calibrationfile'] = 'cal.json'
    apparatus['information']['ink calibration'] = {}
    apparatus['information']['ink calibration']['time'] = 60

    apparatus['information']['materials'][material] = {}
