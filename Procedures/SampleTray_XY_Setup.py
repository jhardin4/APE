from Core import Procedure


class SampleTray_XY_Setup(Procedure):
    def Prepare(self):
        self.name = 'SampleTray_XY_Setup'
        self.requirements['trayname'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'name of the tray'}
        self.requirements['samplename'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'path to store image'}
        self.requirements['xspacing'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'time to weight before taking picture'}
        self.requirements['yspacing'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'name of the camera to be used'}
        self.requirements['xsamples'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'time to weight before taking picture'}
        self.requirements['ysamples'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'name of the camera to be used'}
        self.requirements['xtray'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'time to weight before taking picture'}
        self.requirements['ytray'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'name of the camera to be used'}
        # Setup Apparatus
        if 'trays' not in self.apparatus['information']:
            self.apparatus['information']['trays'] = {}
            

    def Plan(self):
        # Renaming useful pieces of informaiton
        trayname = self.requirements['trayname']['value']
        samplename = self.requirements['samplename']['value']
        xspacing = self.requirements['xspacing']['value']
        yspacing = self.requirements['yspacing']['value']
        xsamples = self.requirements['xsamples']['value']
        ysamples = self.requirements['ysamples']['value']
        xtray = self.requirements['xtray']['value']
        ytray = self.requirements['ytray']['value']

        # Retreiving necessary device names

        # Retrieving information from apparatus

        # Getting necessary eprocs

        # Assign apparatus addresses to procedures

        # Doing stuff
        # Check is enough information is availible
        xinfo = (xspacing != '') + (xsamples != '') + (xtray != '')
        yinfo = (yspacing != '') + (ysamples != '') + (ytray != '')
        if xinfo < 2 or yinfo < 2:
            raise Exception('Not enough information to construct tray.')
        if xinfo == 3:
            if xtray < xsamples * xspacing:
                raise Exception('Tray length in X cannot contain requested number of samples at target spacing.')
        if yinfo == 3:
            if ytray < ysamples * yspacing:
                raise Exception('Tray length in Y cannot contain requested number of samples at target spacing.')        
        # Handle cases where spacing is not defined
        if xspacing == '':
            xspacing = xtray / xsamples
        if yspacing == '':
            yspacing = ytray / ysamples
        # Handle cases where number of samples is not defined
        if xsamples == '':
            xsamples = int(xtray / xspacing)
        if ysamples == '':
            ysamples = int(ytray / yspacing)
        grid = []
        for x in range(xsamples):
            for y in range(ysamples):
                sample_designation = samplename + 'x' + str(x) + 'y' + str(y)
                grid.append({'X': x * xspacing, 'Y': y * yspacing, 'sample': sample_designation, 'used': False})
        self.apparatus['information']['trays'][trayname] = grid

