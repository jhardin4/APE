#used as class because initialization is not needed ***yet***
class importape:
    
    #serves as a configuration setting
    #will become more robust as temperature and extruder data are deconvolved
    #set for debugging right now
    #WIP!!!!!!!!!!!!!!!!!
    def config ( configpoint ):
        if configpoint == 'thread_count':
            return ( 1 )
        if configpoint == 'line_start':
            return ( 50 )
        if configpoint == 'line_end':
            return ( 110 )
        if configpoint == 'call_file':
            return ( 'test_klein_bottle.gcode' )
        if configpoint == 'callthread':
            return 
        if configpoint == 'threadid':
            return ( 'thread1' )
        if configpoint == 'lineorlayer':
            return ( 'line' )
        if configpoint == 'implicitorexplicitaxes':
            return ( 'explicit' )
        if configpoint == 'implicitorexplicittravel':
            return ( 'implicit' )
        if configpoint == 'fileorraw':
            return ( 'raw' )
        if configpoint == 'UI_line':
            return ( 'no' )
        
    #for later use in parsing threads properly if threading is implimented
    #WIP!!!!!!!!!!!!!!!!!
    def multithreaded ( thread_count, line_start, line_end, callthread, startorend ):
        totallines = line_end - line_start
        threadlinecount = totallines // thread_count
        linestart = ( callthread - 1 ) * threadlinecount + line_start
        lineend = callthread * threadlinecount + line_start
        if startorend == 'start':
            return ( linestart )
        if startorend == 'end':
            return ( lineend )
        
    #for use in configuration later
    #WIP!!!!!!!!!!!!!!!!!!!
    #not yet priority
    def filamentdiameter ():
        return ( 0.4 )
    
    #for use when AI needs to easily modify print perameters layer by layer
    #not in use ATM
    def numberoflines ( call_file, startorend ):
        if startorend == 'start':
            return ( 0 )
        else:
            with open ( call_file, 'r') as gcode:
                for i, l in enumerate ( gcode ):
                    pass
                return ( i )
            
    #WIP!!!!!!!!!!!!!!!!
    #for use when AI needs to easily modify print perameters layer by layer
    #not yet priority
    def layertoline ( call_file, startorend, line_start, line_end ):
        with open ( call_file, 'r' ) as gcode:
            lastline = importape.numberoflines ( call_file, 'end' )
            i = 0
            notz = 0
            pastpoint = nextpoint = [ 0, 0, 0 ]
            toolpathpoint = []
            tempX = tempY = tempZ = 0
            for i in range ( 0, line_end + 1 ):
                tempstr = gcode.readline ()
                if "G1" in tempstr:
                    if "Z" in tempstr:
                        if "E" in tempstr:
                            tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "E" ) - 1 ) ]
                        elif "F" in tempstr:
                            tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                        else:
                            tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
        if startorend == 'start':
            return ( layer_start)
        elif startorend == 'end':
            return ( layer_end )
        else:
            pass