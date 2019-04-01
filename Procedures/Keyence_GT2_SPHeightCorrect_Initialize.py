from Core import Procedure
import Procedures.Keyence_GT2_A3200_MeasureXY


class Keyence_GT2_SPHeightCorrect_Initialize(Procedure):
    def Prepare(self):
        self.name = 'Keyence_GT2_SPHeightCorrect_Initialize'
        self.measureTouch = Procedures.Keyence_GT2_A3200_MeasureXY(self.apparatus, self.executor)
        # Setup Apparatus
        if 'SPHeightCorrect' not in self.apparatus['information']:
            self.apparatus['information']['SPHeightCorrect'] = {'touchprobe_Z@start': '', 'original @starts': {}}

    def Plan(self):
        # Renaming useful pieces of informaiton
        alignments = self.apparatus['information']['alignments']
        o_starts = self.apparatus['information']['SPHeightCorrect']['original @starts']

        # Retreiving necessary device names
        motionname = self.apparatus.findDevice({'descriptors': 'motion'})

        # Getting necessary eprocs

        # Assign apparatus addresses to procedures
        
        # Doing stuff
        for alignment in alignments:
            if '@start' in alignment:
                toolname = alignment.split('@')[0]
                if toolname in self.apparatus['devices'][motionname]:
                    if 'axismask' in self.apparatus['devices'][motionname][toolname]:
                        axismask = self.apparatus.getValue(['devices', motionname, toolname, 'axismask'])
                        o_starts[alignment] = {axismask['Z']: alignments[alignment][axismask['Z']]}

        self.measureTouch.Do({'point': {'X': 0, 'Y': 0}})

        self.apparatus.setValue(['information', 'SPHeightCorrect', 'touchprobe_Z@start'], self.apparatus.getValue(['information', 'height_data'])[0])

