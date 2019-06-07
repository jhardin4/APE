def Build_FlexPrinter(materials, tools, apparatus):
    
    #General Printer settings
    devices = {}
    devices['gantry']={'type':'Aerotech_A3200_FlexPrinter', 'model':'Flex Printer', 'descriptors':['motion'],'addresstype':'pointer'}
    devices['gantry']['default'] = {'speed':40, 'length_units':'mm', 'MotionRamp':1000, 'MaxAccel':1000, 'RelAbs':'Abs', 'LookAhead':True, 'mode':'loadrun', 'axismask':{}}
    apparatus['information']['materials']={}
    apparatus['information']['alignments']={}
    apparatus['information']['alignments']['initial']= {'X':'','Y':'', 'ZZ1':'', 'ZZ2':'', 'ZZ3':'', 'ZZ4':''}
    apparatus['information']['alignmentnames']=['initial']
    apparatus['information']['alignmentsfile']='alignments.json'
    apparatus['information']['calibrationfile']='cal.json'
    apparatus['information']['ink calibration']={}
    apparatus['information']['ink calibration']['time'] = 60
    
    primenozzle = True
    for materialx in materials:
        material = list(materialx)[0]
        zaxis = materialx[material]
        # nozzle devices
        devices['n' + material] = {'ID': '', 'OD': '', 'TraceHeight': '', 'TraceWidth': '', 'type': '', 'addresstype': '', 'descriptors': ['nozzle', material]}
        devices['n' + material + 'slide'] = {'ID': '', 'OD': '', 'type': '', 'addresstype': '', 'descriptors': ['nozzle', material + 'slide']}
        # motion details for nozzles
        devices['gantry']['n' + material] = {'speed': '', 'MotionRamp': devices['gantry']['default']['MotionRamp'], 'MaxAccel': devices['gantry']['default']['MaxAccel']}
        devices['gantry']['n' + material] = {'axismask': {'Z': zaxis}}
        devices['gantry']['n' + material + 'slide'] = {}
        devices['gantry']['n' + material + 'slide'] = {'speed': devices['gantry']['default']['speed'], 'MotionRamp': 1000, 'MaxAccel': 1000}
        devices['gantry']['n' + material + 'slide']['axismask'] = devices['gantry']['n' + material]['axismask']
        # information location for each material
        apparatus['information']['materials'][material] = {}
        apparatus['information']['materials'][material]['calibrated'] = False
        apparatus['information']['materials'][material]['do_pumpcal'] = True
        apparatus['information']['materials'][material]['do_speedcal'] = True
        apparatus['information']['alignmentnames'].append('n' + material + '@mark')
        apparatus['information']['alignments']['n' + material + '@mark'] = {'X': '', 'Y': '', zaxis: ''}
        # treat first nozzle as prime nozzles
        if primenozzle:
            apparatus['information']['alignmentnames'].append('n' + material + '@start')
            apparatus['information']['alignments']['n' + material + '@start'] = {'X': '', 'Y': '', zaxis: ''}
            apparatus['information']['alignmentnames'].append('n' + material + '@cal')
            apparatus['information']['alignments']['n' + material + '@cal'] = {'X': '', 'Y': '', zaxis: ''}
            primenozzle = False

    #pumps
    n = 0
    for materialx in materials:
        devices['pump'+str(n)]={'type':'Nordson_UltimusV', 'COM':'','pressure':0, 'vacuum':0, 'pumprestime':0,'pumpontime':0, 'pumpofftime':0, 'midtime':0, 'addresstype':'pointer','descriptors':[]}
        devices['aeropump'+str(n)]={'type':'Nordson_UltimusV_A3200', 'pumpname':'pump'+str(n), 'A3200name':'gantry', 'IOaxis': 'ZZ1', 'IObit':2 ,'pressure':0, 'vacuum':0, 'pumprestime':0,'pumpontime':0, 'pumpofftime':0, 'midtime':0, 'addresstype':'pointer','descriptors':[]}
        n += 1
    # Tools
    for tool in tools:
        devices[tool['name']] = {}
        devices[tool['name']]['type'] = tool['type']
        if tool['type'] == 'Keyence_GT2_A3200':
            # Default Settings
            devices[tool['name']]['addresstype'] = 'pointer'
            devices[tool['name']]['A3200name'] = 'gantry'
            devices[tool['name']]['systemname'] = 'system'
            devices[tool['name']]['retract'] = True
            devices[tool['name']]['zreturn'] = 5
            devices[tool['name']]['axis'] = tool['axis']
            devices[tool['name']]['DOaxis'] = 'ZZ1'
            devices[tool['name']]['DObit'] = 0
            devices[tool['name']]['AIaxis'] = 'ZZ2'
            devices[tool['name']]['AIchannel'] = 0

            # Alignment information
            devices['gantry'][tool['name']] = {'axismask': {'Z': tool['axis']}}
            apparatus['information']['alignmentnames'].append(tool['name'] + '@mark')
            apparatus['information']['alignments'][tool['name'] + '@mark'] = {'X': '', 'Y': '', tool['axis']: ''}
            apparatus['information']['alignments'][tool['name'] + '@TP_init'] = {'X': -200, 'Y': -250, 'ZZ2': -50}

        if tool['type'] == 'IDS_ueye':
            devices[tool['name']]['addresstype'] = 'pointer'
            devices[tool['name']]['settle_time'] = 5

            # Alignment information
            devices['gantry']['camera'] = {'axismask': {'Z': tool['axis']}}
            apparatus['information']['alignmentnames'].append(tool['name'] + '@mark')
            apparatus['information']['alignments'][tool['name'] + '@mark'] = {'X': '', 'Y': '', tool['axis']: ''}

    # System
    devices['system'] = {'type': 'System', 'addresstype': 'pointer'}
    apparatus['devices'] = devices
    
