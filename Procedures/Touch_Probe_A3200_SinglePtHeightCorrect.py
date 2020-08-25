from Core import Procedure
import Procedures.Touch_Probe_A3200_MeasureXY


class Touch_Probe_A3200_SinglePtHeightCorrect(Procedure):
    def Prepare(self):
        self.name = 'Touch_Probe_A3200_SinglePtHeightCorrect'
        self.requirements['point'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'XY point to measure relative to start',
        }
        self.measureTouch = Procedures.Touch_Probe_A3200_MeasureXY(
            self.apparatus, self.executor
        )
        # Setup Apparatus
        if 'SinglePtHeightCorrect' not in self.apparatus['information']:
            self.apparatus['information']['SinglePtHeightCorrect'] = {
                'touchprobe_Z@start': '',
                'original @starts': {},
            }

    def Plan(self):
        # Renaming useful pieces of informaiton
        point = self.requirements['point']['value']
        alignments = self.apparatus['information']['alignments']
        o_starts = self.apparatus['information']['SinglePtHeightCorrect']['original @starts']
        o_z = self.apparatus['information']['SinglePtHeightCorrect']['touchprobe_Z@start']

        # Retreiving necessary device names
        motionname = self.apparatus.findDevice({'descriptors': 'motion'})

        # Store original @starts in SinglePtHeightCorrect information
        for alignment in alignments:
            if '@start' in alignment:
                toolname = alignment.split('@')[0]
                if toolname in self.apparatus['devices'][motionname]:
                    if 'axismask' in self.apparatus['devices'][motionname][toolname]:
                        axismask = self.apparatus.getValue(
                            ['devices', motionname, toolname, 'axismask']
                        )
                        o_starts[alignment] = {
                            axismask['Z']: alignments[alignment][axismask['Z']]
                        }

        # Go to point, measure and apply correction to alignments
        self.measureTouch.Do({'point': point})
        new_z = self.apparatus.getValue(['information', 'height_data'])[0]
        adjustment = new_z - o_z
        for alignment in alignments:
            if '@start' in alignment:
                if alignment in o_starts:
                    for dim in o_starts[alignment]:
                        alignments[alignment][dim] = (
                            o_starts[alignment][dim] + adjustment
                        )
        self.Report(string='@start alignments adjusted by ' + str(adjustment) + '.')
