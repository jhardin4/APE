from Core import Procedure


class SampleTray_Start(Procedure):
    def Prepare(self):
        self.name = 'SampleTray_Start'
        self.requirements['trayname'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'tray',
        }
        self.requirements['procedure'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'pointer to defiend procedure to be performed at each position in tray',
        }
        # Setup Apparatus
        self.apparatus.createAppEntry(['information', 'trays', 'original_alignments'])

    def Plan(self):
        # Renaming useful pieces of information
        trayname = self.requirements['trayname']['value']
        procedure = self.requirements['procedure']['value']
        tray = self.apparatus.getValue(['information', 'trays', trayname])

        # Retreiving necessary device names

        # Retrieving information from apparatus

        # Getting necessary eprocs

        # Assign apparatus addresses to procedures

        # Doing stuff
        # Store original alignments
        for alignment in self.apparatus.getValue(['information', 'alignments']):
            if '@start' in alignment:
                value = self.apparatus.getValue(
                    ['information', 'alignments', alignment]
                )
                self.apparatus.setValue(
                    ['information', 'trays', 'original_alignments', alignment], value
                )

        # Do experiments
        for position in tray:
            # Update the X and Y for each alignment that needs to be updated
            for alignment in self.apparatus.getValue(['information', 'alignments']):
                # Only change alignments that are toolname@start
                # This keeps the XY shifting between samples from impacting the calibrations/cleaning procedures
                if '@start' in alignment:
                    for dim in self.apparatus.getValue(
                        ['information', 'alignments', alignment]
                    ):
                        if dim in position:
                            new_pos = (
                                self.apparatus.getValue(
                                    [
                                        'information',
                                        'trays',
                                        'original_alignments',
                                        alignment,
                                        dim,
                                    ]
                                )
                                + position[dim]
                            )
                            self.apparatus.setValue(
                                ['information', 'alignments', alignment, dim], new_pos
                            )
            self.Report(string=position['sample'] + ' in progress.')
            procedure.Do({'samplename': position['sample']})
            position['used'] = True
        # Return Alignments to original state
        for alignment in self.apparatus.getValue(['information', 'alignments']):
            if '@start' in alignment:
                value = self.apparatus.getValue(
                    ['information', 'trays', 'original_alignments', alignment]
                )
                self.apparatus.setValue(['information', 'alignments', alignment], value)
