import os, glob, time

#finds and caches mod time of youngest file in file_path
def findcachedmodtimefile ( file_path ):
    #if no file is in file_path, creates a file called initial.txt and modifies it.
    if len ( os.listdir (  '%s/Print_With_APE' % ( os.path.expanduser ( '~' ) ) ) ) == 0:
        initialfileloc = r'%s/Print_With_APE/initial.gcode' % ( os.path.expanduser ( '~' ) )
        with open ( initialfileloc, 'w+' ) as initialfile:
            initialfile.write ( " " )
    #grabs and returns youngest file in file_path
    files = glob.glob ( file_path )
    youngest = sorted ( files, key = os.path.getctime)
    return os.path.getctime ( youngest [ -1 ] )

class runape ( object ):

    #initialize class
    def __init__ ( self, file_path ):
        #cach youngest file mod time within file_path
        self.cachedmodtime = findcachedmodtimefile ( file_path )
        self.filepath = file_path
        self.running = True

    #returns youngest file within file_path or its mod time
    def findfile ( self, fileortime ):
        files = glob.glob ( self.filepath )
        youngest = sorted ( files, key = os.path.getctime)
        if fileortime == 'file':
            #return file name
            return youngest [ -1 ]
        if fileortime == 'time':
            #return file mod time
            return os.path.getctime ( youngest [ -1 ] )

    #runs APE in background
    def runinback ( self ):
        while self.running:
            try:
                time.sleep ( 1 )
                #watches file_path for a change in the youngest file
                if self.watchfolder ( ) == 'execute':
                    #returns 'execute' if a change is found
                    return ( 'execute' )
            except FileNotFoundError:
                print ( ' file not found ' )
            except:
                print ( ' unknown error ' )

    #watches file_path for a change in the youngest file
    #Uses time, so files can be overwritten and it will still work
    def watchfolder ( self ):
        modtime = self.findfile ( 'time' )
        if modtime != self.cachedmodtime:
            self.cachedmodtime = modtime
            #returns 'execute' if a change in modtime of youngest file is seen
            return ( 'execute' )











