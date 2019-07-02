from Core import Procedure


class SPHeightCorrect_Update(Procedure):
    def Prepare(self):
        self.name = 'SPHeightCorrect_Update'
        self.requirements['height'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'height to use for correction'}

    def Plan(self):
        # Renaming useful pieces of informaiton
        height = self.requirements['height']['value']
        alignments = self.apparatus['information']['alignments']
        o_starts = self.apparatus['information']['SPHeightCorrect']['original @starts']
        o_z = self.apparatus['information']['SPHeightCorrect']['touchprobe_Z@start']

        # Retreiving necessary device names

        # Getting necessary eprocs

        # Assign apparatus addresses to procedures
        
        # Doing stuff
        
        new_z = height
        adjustment = new_z - o_z
        for alignment in alignments:
            if '@start' in alignment:
                if alignment in o_starts:
                    for dim in o_starts[alignment]:
                        alignments[alignment][dim] = o_starts[alignment][dim]+adjustment
        self.Report(string='@start alignments adjusted by ' + str(adjustment) + '.')