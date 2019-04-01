from Core import Procedure


class Toolpath_Plot(Procedure):
    def Prepare(self):
        self.name = 'Toolpath_Plot'
        self.requirements['parameters'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'parameters used to generate toolpath'}
        self.requirements['target'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'where to store the toolpath'}
        self.requirements['newfigure'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'Make a new figure?'}
        self.requirements['parameters']['address'] = ['information', 'toolpaths', 'parameters']
        self.requirements['target']['address'] = ['information', 'toolpaths', 'toolpath']
        

    def Plan(self):
        materials = self.requirements['parameters']['value']['materials']
        paths = self.requirements['target']['value'][0]
        newfigure = self.requirements['newfigure']['value']
    
        # Assumes toolpath is a standard toolpath structure 2D or 3D
        # is of form [identifier, color designator, line style designator, linewidth, alpha]
        import matplotlib.pyplot as plt
        import time
        #Determine toolpath dimension
        dim = 0
        n = 0
        while dim == 0:
            if n > len(paths)-1:
                dim = 'none'
            else:
                linekeys = str(paths[n].keys())
                if 'startpoint' in linekeys:
                    dim = len(paths[n]['startpoint'])
                n += 1
        # Fail out if nothing is a recognized motion
        if dim == 'none':
            return 'No motions'
        # Create a new figure of appropriate dimensions
        if newfigure:
            if dim == 2:
                plt.figure()
            if dim == 3:
                plt.figure().add_subplot(111, projection='3d')
        # Go line by line in toolpath and plot it with the formatting from 'materials'
        for line in paths:
            linekeys = str(line.keys())
            if 'startpoint' in linekeys:
                #get formatting
                for material in materials:
                    if line['material'] == material['material']:
                        # 'color': colorcode, 'linestyle': lscode, 'linewidth': linewdith, 'alpha':alphavalue}
                        gcolor = material['color']
                        gls = material['linestyle']
                        gwidth = material['linewidth']
                        galpha = material['alpha']
                        if dim == 2:
                            tempx = [line['startpoint']['X'],line['endpoint']['X']]
                            tempy = [line['startpoint']['Y'],line['endpoint']['Y']]
                            plt.plot(tempx, tempy, color=gcolor, ls=gls, linewidth=gwidth, alpha =galpha)
                        if dim == 3:
                            tempx = [line['startpoint']['X'],line['endpoint']['X']]
                            tempy = [line['startpoint']['Y'],line['endpoint']['Y']]
                            tempz = [line['startpoint']['Z'],line['endpoint']['Z']]               
                            plt.plot(tempx, tempy, tempz, color=gcolor, ls=gls, linewidth=gwidth, alpha =galpha)
        logimagefilename = 'Logs/' + str(int(round(time.time(), 0))) + 'image.png'
        plt.savefig(logimagefilename, dpi=600)
        plt.close()
        plt.clf()