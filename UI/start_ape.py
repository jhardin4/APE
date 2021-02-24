import os, glob, pathlib, shutil

#functions here are used to start/install ape and call functions to run it in background
class startape ( ):
    
    #checks if Print_With_APE exists and determinses if installation is needed
    def checksfile ( self ):
        hfile = os.path.expanduser ( '~' )
        #determines operating system type
        if os.name == 'posix':
            sfile = glob.glob ( '%s/*' % ( hfile ) )
        elif os.name == 'nt':
            sfile = glob.glob ( '%s\*' % ( hfile ) )
        else:
            print ( 'fatal error.  cannot determine OS' )
        i = 0
        sfileout = 0
        #runs first time file system check and install for linux
        if os.name == 'posix':
            for i in range ( len ( sfile ) ):
                if sfile [ i ] != '%s/Print_With_APE' % ( hfile ):
                    pass
                elif sfile [ i ] == '%s/Print_With_APE' % ( hfile ):
                    sfileout = sfileout + 1
            if sfileout == 0:
                os.makedirs ( '%s/Print_With_APE' % ( hfile ) )
                return ( 'ready 0' )
            elif sfileout == 1:
                return ( 'ready 1' )
            elif sfileout > 1:
                return ( 'fatal error' )
        #runs first time file system check and install for linux
        elif os.name == 'nt':
            for i in range ( len ( sfile ) ):
                if sfile [ i ] != '%s\Print_With_APE' % ( hfile ):
                    pass
                elif sfile [ i ] == '%s\Print_With_APE' % ( hfile ):
                    sfileout = sfileout + 1
            if sfileout == 0:
                os.makedirs ( '%s\Print_With_APE' % ( hfile ) )
                return ( 'ready 0' )
            elif sfileout == 1:
                return ( 'ready 1' )
            elif sfileout > 1:
                return ( 'fatal error' )
        else:
            print ( 'fatal error.  cannot determine OS' )
    
    #searches for name in root_folder
    def searchfile ( self, name, root_folder ):
        for root, dirs, files in os.walk( root_folder ):
            if name in files:
                return os.path.join( root, name )
    
    #used for windows shortcut creation
    def makeshortcut ( self, shortcut_name, py_loc, start_in, icon_loc ):
        import win32com
        cmd = win32com.client.Dispatch ( 'WScript.shell' )
        shortcut = cmd.CreateShortCut ( '%s.lnk' % ( start_in ) )
        shortcut.TargetPath = py_loc
        shortcut.IconLocation = icon_loc
        shortcut.save ( )
        
    #installs APE
    def installape ( self ):
        if os.name == 'posix':
            #check if linux OS is new enough to run APE on auto
            basefolder = '/usr/share'
            apefolder = '/usr/share/APE-Master'
            appsfolder = '/usr/share/applications'
            apedesktoploc = '%s/APE.desktop' % ( appsfolder )
            pixmaps = '/usr/share/pixmaps'
            whereami = pathlib.Path ( __file__ ).parent.absolute ( )
            apelogo = '%s/installation_files/APE_logo.png' % ( whereami )
            apedesktop = '%s/installation_files/APE.desktop' % ( whereami )
            
            if pathlib ( appsfolder ).is_dir == True:
                #check for .desktop file and install
                if os.path.isfile ( apedesktoploc ) == True:
                    pass
                else:
                    if os.path.isfile ( pixmaps ) == True:
                        pass
                    else:
                        os.makedirs ( pixmaps )
                    shutil.copyfile ( apelogo, pixmaps )
                    shutil.copyfile ( apedesktop, appsfolder )
            else:
                print ( 'fatal error.  cannot determine OS' )
            #install APE
            if pathlib ( apefolder ) == True:
                pass
            elif pathlib ( apefolder ) == False:
                shutil.copytree ( pathlib.Path ( whereami ).parent.absolute ( ), basefolder )
                
        #installs APE
        if os.name == 'nt':
            #check if windows OS is new enough to run APE on auto
            basefolder = 'C:\Program Files'
            apefolder = 'C:\Program Files\APE-Master'
            appsfolder = 'C:\ProgramData\Microsoft\Windows\Start Menu\Programs'
            apedesktoploc = '%s\APE.bat' % ( appsfolder )
            pythonloc = self.searchfile ( 'python.exe', 'C:' )
            whereami = pathlib.Path ( __file__ ).parent.absolute ( )
            apelogo = r'%s\UI\installation_filesAPE_logo.ico' % ( apefolder )
            apedesktop = r'%s\UI\installation_files\APE.bat' % ( apefolder )
            apepy = r'%s\UI_monolith.py' % ( apefolder )
            
            if pathlib ( apefolder ) == True:
                pass
            elif pathlib ( apefolder ) == False:
                shutil.copytree ( pathlib.Path ( whereami ).parent.absolute ( ), basefolder )
                
            if pathlib ( basefolder ).is_dir == True:
                #check for .bat file and install
                if os.path.isfile ( apedesktoploc ) == True:
                    pass
                else:
                    #make apedesktop point to correct folders and icons
                    writetofile = open ( 'apedesktop', 'w' )
                    writetofile.write ( '"%s"' % ( pythonloc ), '"%s"' % ( apepy ) )
                    writetofile.write ( 'pause' )
                    writetofile.close ( )
                    self.makeshortcut ( 'APE', apedesktop, appsfolder, apelogo )
            else:
                print ( 'fatal error.  cannot determine OS' )