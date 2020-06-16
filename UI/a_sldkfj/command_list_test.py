import threading
from .import_ape import importape
from .run_ape import runape


class getape ( threading.Thread ):
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
        if call_file == 'auto':
            self.call_file = runape ( '/home/nicholasarn/Print_With_APE/*.gcode' ).findfile ( 'file' )
        else:
            self.call_file = call_file
#        self.thread_number = importape.getthreadcount
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

    def multithreadpoint ( thread_count, call_thread, call_file, implicitorexplicitaxes, implicitorexplicittravel,  lineorlayer, line_start, line_end, fileorraw ):
        multipointlist = getape.point ( call_file, implicitorexplicitaxes, implicitorexplicittravel, lineorlayer, importape.multithreaded( thread_count, line_start, line_end, call_thread, 'start' ), importape.multithreaded( thread_count, line_start, line_end, call_thread, 'end' ), 'raw' )
        return ( multipointlist )

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
    #    getape.runpoint ( call_file, implicitorexplicitaxes, implicitorexplicittravel,  lineorlayer, line_start, line_end, fileorraw )

    #def runpoint ( call_file, implicitorexplicitaxes, implicitorexplicittravel,  lineorlayer, line_start, line_end, fileorraw ):
        with open ( call_file, 'r' ) as gcode:
            pastpoint  = nextpoint = [ 0, 0, 0 ]
            pastpoint2 = [ 0, 0, 0 ]
            toolpathpoint = []
            linepoint = { 'X' : 0, 'Y' : 0, 'Z' : 0 }
            #{ 'X' : 0, 'Y' : 0, 'Z' : 0 }
            tempX = tempY = tempZ = 0
            i = 0
            for i in range ( 0, line_start ):
                gcode.readline ()
                i = i + 1
    #       for line in gcode:
    #           tempstr = line
    #           print ( tempstr )
            i = 0
            for i in range ( line_start, line_end + 1 ):
                tempstr = gcode.readline ()
                if "G1" in tempstr:
                    #print ( tempstr )
                    if "X" in tempstr and "Y" in tempstr and "Z" in tempstr:
                        tempX = tempstr [ ( tempstr.find ( "X" ) + 1 ) : ( tempstr.find ( "Y" ) - tempstr.find ( "X" ) - 1 + tempstr.find ( "X" ) ) ]
                        #print ( "1X:", tempX )
                        tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( tempstr.find ( "Z" ) - tempstr.find ( "Y" ) - 1 + tempstr.find ( "Y" ) ) ]
                        #print ( "1Y:", tempY )
                        if "E" in tempstr:
                            tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "E" ) - 1 ) ]
                        elif "F" in tempstr:
                            tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                        else:
                            tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                        #print ( "1Z:", tempZ )
                    elif "X" in tempstr and "Y" in tempstr:
                        tempX = tempstr [ ( tempstr.find ( "X" ) + 1 ) : ( tempstr.find ( "Y" ) - tempstr.find ( "X" ) - 1 + tempstr.find ( "X" ) ) ]
                        #print ( "2X:", tempX )
                        if "E" in tempstr:
                            tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( tempstr.find ( "E" ) - 1 ) ]
                        elif "F" in tempstr:
                            tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                        else:
                            tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                        #print ( "2Y:", tempY )
                    elif "X" in tempstr and "Z" in tempstr:
                        tempX = tempstr [ ( tempstr.find ( "X" ) + 1 ) : ( tempstr.find ( "Y" ) - tempstr.find ( "X" ) - 1 + tempstr.find ( "X" ) ) ]
                        #print ( "3X:", tempX )
                        if "E" in tempstr:
                            tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "E" ) - 1 ) ]
                        elif "F" in tempstr:
                            tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                        else:
                            tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                        #print ( "3Z:", tempZ )
                    elif "Y" in tempstr and "Z" in tempstr:
                        tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( tempstr.find ( "Z" ) - tempstr.find ( "Y" ) - 1 + tempstr.find ( "Y" ) ) ]
                        #print ( "4Y:", tempY )
                        if "E" in tempstr:
                            tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "E" ) - 1 ) ]
                        elif "F" in tempstr:
                            tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                        else:
                            tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                        #print ( "4Z:", tempZ )
                    elif "X" in tempstr:
                        if "E" in tempstr:
                            tempX = tempstr [ ( tempstr.find ( "X" ) + 1 ) : ( tempstr.find ( "E" ) - 1 ) ]
                        elif "F" in tempstr:
                            tempX = tempstr [ ( tempstr.find ( "X" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                        else:
                            tempX = tempstr [ ( tempstr.find ( "X" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                        #print ( "5X:", tempX )
                    elif "Y" in tempstr:
                        if "E" in tempstr:
                            tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( tempstr.find ( "E" ) - 1 ) ]
                        elif "F" in tempstr:
                            tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                        else:
                            tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                        #print ( "6Y:", tempY )
                    elif "Z" in tempstr:
                        if "E" in tempstr:
                            tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "E" ) - 1 ) ]
                        elif "F" in tempstr:
                            tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                        else:
                            tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                        #print ( "7Z:", tempZ )
                    #print ( "pastpoint:", pastpoint )
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
                    elif "E" in tempstr:
                        pass
                    #if implicitorexplicittravel == 'implicit':
                    #    if "E" not in tempstr:
                    #        pass
                    #    else:
                    #        if implicitorexplicitaxes == 'implicit':
                    #            nextpoint [ 0 ] = pastpoint [ 0 ] + float ( tempX )
                    #            nextpoint [ 1 ] = pastpoint [ 1 ] + float ( tempY )
                    #            nextpoint [ 2 ] = pastpoint [ 2 ] + float ( tempZ )
                    #            pastpoint[ 0 ] = nextpoint[ 0 ]
                    #            pastpoint[ 1 ] = nextpoint[ 1 ]
                    #            pastpoint[ 2 ] = nextpoint[ 2 ]
                    #        if implicitorexplicitaxes == 'explicit':
                    #            nextpoint [ 0 ] = float ( tempX )
                    #            nextpoint [ 1 ] = float ( tempY )
                    #            nextpoint [ 2 ] = float ( tempZ )
                    #        elif "E" in tempstr:
                    #            pass
                    #if implicitorexplicittravel == 'explicit':
                    #    if implicitorexplicitaxes == 'implicit':
                    #            nextpoint [ 0 ] = pastpoint [ 0 ] + float ( tempX )
                    #            nextpoint [ 1 ] = pastpoint [ 1 ] + float ( tempY )
                    #            nextpoint [ 2 ] = pastpoint [ 2 ] + float ( tempZ )
                    #            pastpoint[ 0 ] = nextpoint[ 0 ]
                    #            pastpoint[ 1 ] = nextpoint[ 1 ]
                    #            pastpoint[ 2 ] = nextpoint[ 2 ]
                    #    if implicitorexplicitaxes == 'explicit':
                    #        nextpoint [ 0 ] = float ( tempX )
                    #        nextpoint [ 1 ] = float ( tempY )
                    #        nextpoint [ 2 ] = float ( tempZ )
                    #    else:
                    #        pass
                    #else:
                    #    pass

                    #print ( "nextpoint:", nextpoint )
                    #tempX = tempY = tempZ = 0
                    linepoint = { 'X' : nextpoint [ 0 ], 'Y' : nextpoint [ 1 ], 'Z' : nextpoint [ 2 ] }
                    #print ( linepoint )
                    if i in range ( line_start, line_end + 1 ):
                        if 'X' in tempstr or 'Y' in tempstr or 'Z' in tempstr:
                            toolpathpoint.append ( linepoint )
                        else:
                            pass
                    #pastpoint2[ 0 ] = nextpoint[ 0 ]
                    #pastpoint2[ 1 ] = nextpoint[ 1 ]
                    #pastpoint2[ 2 ] = nextpoint[ 2 ]
                #print ( "----------------------------------------------------------------------------------------" )
            i = 0
            if fileorraw == 'raw':
                return ( toolpathpoint )
            else:
                return ( toolpathpoint )

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


#test = getape( 'name', 'test_klein_bottle.gcode')
#test = getape( 'auto' )
#print ( test.start () )
#print ( test.run ( ) )
#print ( getape.point ( 'test_klein_bottle.gcode', 'explicit', 'implicit', 'line', 100, 100, 'raw' ) )
#print ( getape.multithreadpoint ( 2, 1, 'test_klein_bottle.gcode', 'explicit', 'implicit', 'line', 100, 100, 'raw' ) )
#print ( getape.extrude ( 'test_klein_bottle.gcode', 'line', 0, 80, 'distance', 'raw' ) )

#print ( getape.code ( 'test_klein_bottle.gcode', 'line', 0, 80, 'distance', 'raw' ) )
    #input ( "press enter to continue" )
