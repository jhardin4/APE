from Core import Procedure
import Procedures.Keyence_GT2_A3200_MeasureXY


class Keyence_GT2_SPHeightCorrect_Correct(Procedure): 
    def Prepare(self):
        self.name = 'Keyence_GT2_SPHeightCorrect_Correct'
        self.requirements['point'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'XY point to measure relative to start'}
        self.measureTouch = Procedures.Keyence_GT2_A3200_MeasureXY(self.apparatus, self.executor)

    def Plan(self):
        # Renaming useful pieces of informaiton
        point = self.requirements['point']['value']
        alignments = self.apparatus['information']['alignments']
        o_starts = self.apparatus['information']['SPHeightCorrect']['original @starts']
        o_z = self.apparatus['information']['SPHeightCorrect']['touchprobe_Z@start']

        # Retreiving necessary device names

        # Getting necessary eprocs

        # Assign apparatus addresses to procedures
        
        # Doing stuff
        self.measureTouch.Do({'point': point})
        new_z = self.apparatus.getValue(['information', 'height_data'])[0]
        adjustment = new_z - o_z
        for alignment in alignments:
            if '@start' in alignment:
                if alignment in o_starts:
                    for dim in o_starts[alignment]:
                        alignments[alignment][dim] = o_starts[alignment][dim]+adjustment
        self.Report(string='@start alignments adjusted by ' + str(adjustment) + '.')
