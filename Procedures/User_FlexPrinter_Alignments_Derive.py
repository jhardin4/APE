from Core import Procedure
import Procedures.User_Consol_Input


class User_FlexPrinter_Alignments_Derive(Procedure):
    def Prepare(self):
        self.name = 'User_FlexPrinter_Alignments_Derive'
        self.requirements['Measured_List'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'list of measurements',
        }
        self.requirements['primenoz'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'prime material',
        }
        self.requirements['loptions'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'optional list for just doing a subset of locations',
        }
        self.userinput = Procedures.User_Consol_Input(self.apparatus, self.executor)

    def Plan(self):
        measuredlist = self.requirements['Measured_List']['value']
        primenoz = self.requirements['primenoz']['value']
        alignments = self.apparatus.getValue(['information', 'alignments'])

        motionname = self.apparatus.findDevice(descriptors='motion')

        # Check that the alignments are valid and return results of analysis
        cur_alignments = alignments
        missing_alignments = []
        incomplete_alignments = []
        for alignment in measuredlist:
            if alignment not in cur_alignments:
                missing_alignments.append(alignment)
            else:
                incomplete = False
                for dim in cur_alignments[alignment]:
                    if not isinstance(cur_alignments[alignment][dim], (int, float)):
                        incomplete = True
                if incomplete:
                    incomplete_alignments.append(alignment)
        message = ''
        if len(missing_alignments) > 0:
            message += 'Missing Alignments:\n'
            message += str(missing_alignments)
        if len(incomplete_alignments) > 0:
            message += 'Incomplete Alignments:\n'
            message += str(incomplete_alignments)
        default = ''
        if message != '':
            self.userinput.Do({'message': message, 'default': default})
            if self.loptions == '':
                return

        toollist = [n.split('@')[0] for n in measuredlist]
        loclist = ['start', 'cal', 'clean', 'mark']
        for dim in alignments['initial'].keys()^['X','Y']:
            loclist.append('safe' + dim)
        if self.loptions == '':
            self.loptions = loclist
        optionList = {}
        for loc in loclist:
            if loc in self.loptions:
                optionList[loc] = True
            else:
                optionList[loc] = False
        # print(str(optionList))
        # Doing stuff
        # Set up safety positions for Z-axis (not XY) without restricting axis names
        for axis in alignments['initial'].keys()^['X','Y']:
            if 'safe' + axis in self.loptions:
                if optionList['safe'+axis]:
                    alignments['safe'+axis] = {axis: alignments['initial'][axis]}
        
        
        toollist.remove('initial')

        paxismask = self.apparatus.getValue(
            ['devices', motionname, primenoz, 'axismask']
        )
        pzaxis = 'Z'
        if 'Z' in paxismask:
            pzaxis = paxismask['Z']

        for tool in toollist:
            zaxis = 'Z'
            axismask = self.apparatus.getValue(
                ['devices', motionname, tool, 'axismask']
            )
            if 'Z' in axismask:
                zaxis = axismask['Z']

            for name in [tool + '@start', tool + 'slide@start', tool + '@cal', tool + '@clean']:
                if name not in alignments:
                    alignments[name] = {}

            if optionList['start']:
                alignments[tool + '@start']['X'] = alignments[primenoz + '@start']['X'] - (
                    alignments[primenoz + '@mark']['X'] - alignments[tool + '@mark']['X']
                )
                alignments[tool + '@start']['Y'] = alignments[primenoz + '@start']['Y'] - (
                    alignments[primenoz + '@mark']['Y'] - alignments[tool + '@mark']['Y']
                )
                alignments[tool + '@start'][zaxis] = alignments[primenoz + '@start'][
                    pzaxis
                ] - (
                    alignments[primenoz + '@mark'][pzaxis]
                    - alignments[tool + '@mark'][zaxis]
                )
                alignments[tool + 'slide@start'] = alignments[tool + '@start']
            
            if optionList['cal']:
                alignments[tool + '@cal']['X'] = alignments[primenoz + '@cal']['X'] - (
                    alignments[primenoz + '@mark']['X'] - alignments[tool + '@mark']['X']
                )
                alignments[tool + '@cal']['Y'] = alignments[primenoz + '@cal']['Y'] - (
                    alignments[primenoz + '@mark']['Y'] - alignments[tool + '@mark']['Y']
                )
                alignments[tool + '@cal'][zaxis] = alignments[primenoz + '@cal'][pzaxis] - (
                    alignments[primenoz + '@mark'][pzaxis]
                    - alignments[tool + '@mark'][zaxis]
                )
            
            if optionList['clean']:
                alignments[tool + '@clean']['X'] = alignments[primenoz + '@clean']['X'] - (
                    alignments[primenoz + '@mark']['X'] - alignments[tool + '@mark']['X']
                )
                alignments[tool + '@clean']['Y'] = alignments[primenoz + '@clean']['Y'] - (
                    alignments[primenoz + '@mark']['Y'] - alignments[tool + '@mark']['Y']
                )
                alignments[tool + '@clean'][zaxis] = alignments[primenoz + '@clean'][pzaxis] - (
                    alignments[primenoz + '@mark'][pzaxis]
                    - alignments[tool + '@mark'][zaxis]
                )

        self.apparatus.setValue(['information', 'alignments'], alignments)
