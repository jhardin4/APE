import threading, os
from .import_ape import importape
from .run_ape import runape

#primary deconvolving solution
class getape ( threading.Thread ):
    #initializes the class
    def __init__ ( self, call_file ):
        threading.Thread.__init__( self )
        self.thread_id = 'name'
        self.thread_count = importape.config ( 'thread_count' )
        self.implicitorexplicitaxes = importape.config ( 'implicitorexplicitaxes' )
        self.implicitorexplicittravel = importape.config ( 'implicitorexplicittravel' )
        self.lineorlayer = importape.config ( 'lineorlayer' )
        self.line_start = importape.config ( 'line_start' )
        self.line_end = importape.config ( 'line_end' )
        self.fileorraw = importape.config ( 'fielorraw' )
        #used for selecting file path behavior of getape.xxx
        if call_file == 'auto':
            self.call_file = runape ( '%s/Print_With_APE/*.gcode' % ( os.path.expanduser ( '~' ) ) ).findfile ( 'file' )
        else:
            self.call_file = call_file
#        self.thread_number = importape.getthreadcount
    
    #used in this manner so that threading can be implimented for decreasing processing time later
    def run ( self ):
        thread_id = importape.config ( 'thread_id' )
        thread_count = self.thread_count
        implicitorexplicitaxes = self.implicitorexplicitaxes
        implicitorexplicittravel = self.implicitorexplicittravel
        lineorlayer = self.lineorlayer
        line_start = self.line_start
        line_end = self.line_end
        fileorraw = self.fileorraw
        call_file = self.call_file
        call_thread = 1
        #threadlock = threading.Lock ()
        #threadlock.aquire ()
        return ( getape.multithreadpoint ( thread_count, call_thread, call_file, implicitorexplicitaxes, implicitorexplicittravel,  lineorlayer, line_start, line_end, fileorraw ) )
        #threadlock.release ()

    #used for splitting up threads properly if threading is implimented
    def multithreadpoint ( thread_count, call_thread, call_file, implicitorexplicitaxes, implicitorexplicittravel,  lineorlayer, line_start, line_end, fileorraw ):
        multipointlist = getape.point ( call_file, implicitorexplicitaxes, implicitorexplicittravel, lineorlayer, importape.multithreaded( thread_count, line_start, line_end, call_thread, 'start' ), importape.multithreaded( thread_count, line_start, line_end, call_thread, 'end' ), 'raw' )
        return ( multipointlist )

    #gets the points needed from gcode
    def point ( call_file, implicitorexplicitaxes, implicitorexplicittravel,  lineorlayer, line_start, line_end, fileorraw ):
        if lineorlayer == 'layer':
            templine_start = importape.layertoline ( call_file, 'start', line_start, line_end )
            templine_end = importape.layertoline ( call_file, 'end', line_start, line_end )
            line_start = templine_start
            line_end = templine_end
        if line_start == 'start':
            line_start = importape.numberoflines ( call_file, 'start' )
        if line_end == 'end':
            line_end = importape.numberoflines ( call_file, 'end' )
        with open ( call_file, 'r' ) as gcode:
            pastpoint  = nextpoint = [ 0, 0, 0 ]
            pastpoint2 = [ 0, 0, 0 ]
            toolpathpoint = []
            linepoint = { 'X' : 0, 'Y' : 0, 'Z' : 0 }
            tempX = tempY = tempZ = 0
            i = 0
            for i in range ( 0, line_start ):
                gcode.readline ()
                i = i + 1
            i = 0
            for i in range ( line_start, line_end + 1 ):
                tempstr = gcode.readline ()
                if "G1" in tempstr:
                    if "X" in tempstr and "Y" in tempstr and "Z" in tempstr:
                        tempX = tempstr [ ( tempstr.find ( "X" ) + 1 ) : ( tempstr.find ( "Y" ) - tempstr.find ( "X" ) - 1 + tempstr.find ( "X" ) ) ]
                        tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( tempstr.find ( "Z" ) - tempstr.find ( "Y" ) - 1 + tempstr.find ( "Y" ) ) ]
                        if "E" in tempstr:
                            tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "E" ) - 1 ) ]
                        elif "F" in tempstr:
                            tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                        else:
                            tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                        #print ( "1Z:", tempZ )
                    elif "X" in tempstr and "Y" in tempstr:
                        tempX = tempstr [ ( tempstr.find ( "X" ) + 1 ) : ( tempstr.find ( "Y" ) - tempstr.find ( "X" ) - 1 + tempstr.find ( "X" ) ) ]
                        if "E" in tempstr:
                            tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( tempstr.find ( "E" ) - 1 ) ]
                        elif "F" in tempstr:
                            tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                        else:
                            tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                    elif "X" in tempstr and "Z" in tempstr:
                        tempX = tempstr [ ( tempstr.find ( "X" ) + 1 ) : ( tempstr.find ( "Y" ) - tempstr.find ( "X" ) - 1 + tempstr.find ( "X" ) ) ]
                        if "E" in tempstr:
                            tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "E" ) - 1 ) ]
                        elif "F" in tempstr:
                            tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                        else:
                            tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                    elif "Y" in tempstr and "Z" in tempstr:
                        tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( tempstr.find ( "Z" ) - tempstr.find ( "Y" ) - 1 + tempstr.find ( "Y" ) ) ]
                        if "E" in tempstr:
                            tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "E" ) - 1 ) ]
                        elif "F" in tempstr:
                            tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                        else:
                            tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                    elif "X" in tempstr:
                        if "E" in tempstr:
                            tempX = tempstr [ ( tempstr.find ( "X" ) + 1 ) : ( tempstr.find ( "E" ) - 1 ) ]
                        elif "F" in tempstr:
                            tempX = tempstr [ ( tempstr.find ( "X" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                        else:
                            tempX = tempstr [ ( tempstr.find ( "X" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                    elif "Y" in tempstr:
                        if "E" in tempstr:
                            tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( tempstr.find ( "E" ) - 1 ) ]
                        elif "F" in tempstr:
                            tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                        else:
                            tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                    elif "Z" in tempstr:
                        if "E" in tempstr:
                            tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "E" ) - 1 ) ]
                        elif "F" in tempstr:
                            tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                        else:
                            tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                    if implicitorexplicitaxes == 'implicit':
                        nextpoint [ 0 ] = pastpoint [ 0 ] + float ( tempX )
                        nextpoint [ 1 ] = pastpoint [ 1 ] + float ( tempY )
                        nextpoint [ 2 ] = pastpoint [ 2 ] + float ( tempZ )
                        pastpoint[ 0 ] = nextpoint[ 0 ]
                        pastpoint[ 1 ] = nextpoint[ 1 ]
                        pastpoint[ 2 ] = nextpoint[ 2 ]
                    if implicitorexplicitaxes == 'explicit':
                        nextpoint [ 0 ] = float ( tempX )
                        nextpoint [ 1 ] = float ( tempY )
                        nextpoint [ 2 ] = float ( tempZ )
                    #needed for extruder information later.  possible to move into different deconvolver
                    elif "E" in tempstr:
                        pass
                    linepoint = { 'X' : nextpoint [ 0 ], 'Y' : nextpoint [ 1 ], 'Z' : nextpoint [ 2 ] }
                    if i in range ( line_start, line_end + 1 ):
                        if 'X' in tempstr or 'Y' in tempstr or 'Z' in tempstr:
                            toolpathpoint.append ( linepoint )
                        else:
                            pass
            i = 0
            if fileorraw == 'raw':
                return ( toolpathpoint )
            else:
                return ( toolpathpoint )

    #gets extrusion information
    #Broken in current state and not in use
    def extrude ( call_file, lineorlayer, line_start, line_end, distancevolumeorpressure, fileorraw ):
        if lineorlayer == 'layer':
            templine_start = importape.layertoline ( call_file, 'start', line_start, line_end )
            templine_end = importape.layertoline ( call_file, 'end', line_start, line_end )
            line_start = templine_start
            line_end = templine_end
        if line_start == 'start':
            line_start = importape.numberoflines ( call_file, 'start' )
        if line_end == 'end':
            line_end = importape.numberoflines ( call_file, 'end' )
        with open ( call_file, 'r' ) as gcode:
            i = 0
            pi = 3.1415926
            toolpathextrude = []
            pastline = nextline = [ 0, 0 ]
            tempE = tempF = 0
            for i in range ( 0, line_end + 1 ):
                tempstr = gcode.readline ()
                if i in range ( line_start, line_end + 1 ):
                    if "G1" in tempstr:
                        if "E" in tempstr and "F" in tempstr:
                            tempE = tempstr [ ( tempstr.find ( "E" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                            tempF = tempstr [ ( tempstr.find ( "F" ) +1 ) : ( len ( tempstr ) + 2 ) ]
                        elif "E" in tempstr:
                            tempE = tempstr [ ( tempstr.find ( "E" ) +1 ) : ( len ( tempstr ) + 2 ) ]
                        elif "F" in tempstr:
                            tempF = tempstr [ ( tempstr.find ( "F" ) +1 ) : ( len ( tempstr ) + 2 ) ]
                    nextline [ 0 ] = float ( tempE )
                    if tempF != 0:
                        nextline [ 1 ] = float ( tempF )
                    else:
                        nextline [ 1 ] = pastline [ 1 ]
                    pastline [ 0 ] = nextline [ 0 ]
                    pastline [ 1 ] = nextline [ 1 ]
                    tempE = tempF = 0
                    if distancevolumeorpressure == 'volume':
                        lineextrude = { 'E' : nextline [ 0 ] * importape.filamentdiameter () * pi, 'F' : nextline [ 1 ] * importape.filamentdiameter () * pi }
                        toolpathextrude.append ( lineextrude )
                    elif distancevolumeorpressure == 'pressure': #maybe???????????????????????????
                        lineextrude = { 'E' : nextline [ 0 ], 'F' : nextline [ 1 ] }
                        toolpathextrude.append ( lineextrude )
                    elif distancevolumeorpressure == 'distance':
                        lineextrude = { 'E' : nextline [ 0 ], 'F' : nextline [ 1 ] }
                        toolpathextrude.append ( lineextrude )
            i = 0
            if fileorraw == 'raw':
                return ( toolpathextrude )
            else:
                return ( toolpathextrude )

    #origonally supposed to parse multiple pointlists together
    #Not in use but could have use if threading is implimented
    def code ( call_file, lineorlayer, line_start, line_end, distancevolumeorpressure, fileorraw ):
        if lineorlayer == 'layer':
            templine_start = importape.layertoline ( call_file, 'start', line_start, line_end )
            templine_end = importape.layertoline ( call_file, 'end', line_start, line_end )
            line_start = templine_start
            line_end = templine_end
        if line_start == 'start':
            line_start = importape.numberoflines ( call_file, 'start' )
        if line_end == 'end':
            line_end = importape.numberoflines ( call_file, 'end' )
        toolpath3D = []
        #toolpath3D.append ( { 'parse': 'start' } )
        tempextrude = { 'E' : 0, 'F' : 0 }
        temppoint = { 'X' : 0, 'Y' : 0, 'Z' : 0 }
        for i in range ( line_start, line_end + 1 ):
            if getape.extrude ( call_file, lineorlayer, i, i, distancevolumeorpressure, 'raw' ) [ 0 ] != []:
                tempextrude = getape.extrude ( call_file, lineorlayer, i, i, distancevolumeorpressure, 'raw' ) [ 0 ]
            if getape.point ( call_file, lineorlayer, i, i, 'raw' ) != []:
                temppoint = getape.point ( call_file, lineorlayer, i, i, 'raw' ) [ 0 ]
            #toolpath3D.append ( tempextrude )
            toolpath3D.append ( temppoint )
        #toolpath3D.append ( { 'parse': 'end' } )
        return ( toolpath3D )