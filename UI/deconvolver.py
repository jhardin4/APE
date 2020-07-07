import threading, os
from import_ape import importape
from run_ape import runape

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
        self.fileorraw = importape.config ( 'fileorraw' )
        #used for selecting file path behavior of getape.xxx
        if call_file == 'auto':
            self.call_file = runape ( '%s/Print_With_APE/*.gcode' % ( os.path.expanduser ( '~' ) ) ).findfile ( 'file' )
        else:
            self.call_file = call_file
#        self.thread_number = importape.getthreadcount
    
    #used in this manner so that threading can be implimented for decreasing processing time later
    def run ( self ):
        thread_id = importape.config ( 'thread_    #returns dictionaryid' )
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

    #deconvolves spatial points
    #returns dictionary
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
    
    #deconvolves hotend heat, system fan, bridging fan, tool change, tool #, multiplexer #, and tool change distance information
    #returns dictionary
    def hotend ( call_file, lineorlayer, line_start, line_end, initialize, fileorraw ):
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
            p = 0
            pastline = [ 0, 0, 0, '', 1, 1, '', 0 ]
            nextline = [ 0, 0, 0, '', 1, 1, '', 0 ]
            hotendline = { 'H' : 0, 'SF' : 0, 'BF' : 0, 'TC' : '', 'T' : 1, 'MX' : 1, 'MXA' : '', 'D' : 0 }
            hotendfinal = [ ]
            temph = tempfan = tempsf = tempbf = temptmx = tempt = tempmx = tempd = 0
            temptc = tempmxa = ''
            if initialize == 'yes':
                line_end = 100
            for i in range ( 0, line_start ):
                gcode.readline ()
                i = i + 1
            i = 0
            for i in range ( 0, line_end + 1 ):
                tempstr = gcode.readline ()
                if i in range ( line_start, line_end + 1 ):
                    if "M104" in tempstr or "M109" in tempstr:
                        if "S" in tempstr:
                            if ";" in tempstr:
                                temph = tempstr [ ( tempstr.find ( "S" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
                            else:
                                temph = tempstr [ ( tempstr.find ( "S" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                        else:
                            temph = 0
                    if "M106" in tempstr:
                        if "P" in tempstr and "S" in tempstr:
                            tempfan = tempstr [ ( tempstr.find ( "P" ) + 1 ) : ( tempstr.find ( "S" ) - 1 ) ]
                            if tempfan == 1:
                                if ";" in tempstr:
                                    tempbf = tempstr [ ( tempstr.find ( "S" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
                                else:
                                    tempbf = tempstr [ ( tempstr.find ( "S" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                            elif tempfan == 2:
                                if ";" in tempstr:
                                    tempsf = tempstr [ ( tempstr.find ( "S" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
                                else:
                                    tempsf = tempstr [ ( tempstr.find ( "S" ) + 1) : ( len ( tempstr ) + 2 ) ]
                        elif "S" in tempstr:
                            if ";" in tempstr:
                                tempbf = tempstr [ ( tempstr.find ( "S" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
                            else:
                                tempbf = tempstr [ ( tempstr.find ( "S" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                    if "M107" in tempstr:
                        tempbf = 0
                    if "M600" in tempstr:
                        if "AUTO" in tempstr:
                            tempmxa = 'AUTO'
                        else:
                            temptc = 'USR Load'
                    if "M701" in tempstr:
                        if "T" in tempstr and "L" in tempstr:
                            temptmx = tempstr [ ( tempstr.find ( "T" ) + 1 ) : ( tempstr.find ( "L" ) - 1 ) ]
                            if ";" in tempstr:
                                tempd = tempstr [ ( tempstr.find ( "L" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
                            else:
                                tempd = tempstr [ ( tempstr.find ( "L" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                        elif "L" in tempstr:
                            if "Z" in tempstr:
                                tempd = tempstr [ ( tempstr.find ( "L" ) + 1 ) : ( tempstr.find ( "Z" ) - 1 ) ]
                            else:
                                if ";" in tempstr:
                                    tempd = tempstr [ ( tempstr.find ( "L" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
                                else:
                                    tempd = tempstr [ ( tempstr.find ( "L" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                        elif "T" in tempstr:
                            if "Z" in tempstr:
                                temptmx = tempstr [ ( tempstr.find ( "T" ) + 1 ) : ( tempstr.find ( "Z" ) - 1 ) ]
                            else:
                                if ";" in tempstr:
                                    temptmx = tempstr [ ( tempstr.find ( "T" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
                                else:
                                    temptmx = tempstr [ ( tempstr.find ( "T" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                        if tempmxa == 'AUTO':
                            tempmx = temptmx
                        else:
                            tempt = temptmx
                        temptc = 'load'
                    if "M702" in tempstr:
                        if "T" in tempstr and "U" in tempstr:
                            tempmx = tempstr [ ( tempstr.find ( "T" ) + 1 ) : ( tempstr.find ( "U" ) - 1 ) ]
                            if ";" in tempstr:
                                tempd = tempstr [ ( tempstr.find ( "U" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
                            else:
                                tempd = tempstr [ ( tempstr.find ( "U" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                        elif "U" in tempstr:
                            if "Z" in tempstr:
                                tempd = tempstr [ ( tempstr.find ( "U" ) + 1 ) : ( tempstr.find ( "Z" ) - 1 ) ]
                            else:
                                if ";" in tempstr:
                                    tempd = tempstr [ ( tempstr.find ( "U" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
                                else:
                                    tempd = tempstr [ ( tempstr.find ( "U" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                        elif "T" in tempstr:
                            if "Z" in tempstr:
                                tempmx = tempstr [ ( tempstr.find ( "T" ) + 1 ) : ( tempstr.find ( "Z" ) - 1 ) ]
                            else:
                                if ";" in tempstr:
                                    tempmx = tempstr [ ( tempstr.find ( "T" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
                                else:
                                    tempmx = tempstr [ ( tempstr.find ( "T" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                        if tempmxa == 'AUTO':
                            tempmx = temptmx
                        else:
                            tempt = temptmx
                        temptc = 'unload'
                    if pastline [ 0 ] != temph:
                        nextline [ 0 ] = temph
                    if pastline [ 1 ] != tempsf:
                        nextline [ 1 ] = tempsf
                    if pastline [ 2 ] != tempbf:
                        nextline [ 2 ] = tempbf
                    if pastline [ 3 ] != temptc:
                        nextline [ 3 ] = temptc
                    if pastline [ 4 ] != tempt:
                        nextline [ 4 ] = tempt
                    if pastline [ 5 ] != tempmx:
                        nextline [ 5 ] = tempmx
                    if pastline [ 6 ] != tempmxa:
                        nextline [ 6 ] = tempmxa
                    if pastline [ 7 ] != tempd:
                        nextline [ 7 ] = tempd
                    temptc = ''
                    tempmxa = ''
                    p = 0
                    for p in range ( 0, 7 ):
                        pastline [ p ] = nextline [ p ]
                    hotendline = { 'H' : nextline [ 0 ], 'SF' : nextline [ 1 ], 'BF' : nextline [ 2 ], 'TC' : nextline [ 3 ], 'T' : nextline [ 4 ], 'MX' : nextline [ 5 ], 'MXA' : nextline [ 6 ], 'D' : nextline [ 7 ] }
                    if initialize == 'yes':
                        if 'X' in tempstr or 'Y' in tempstr or 'Z' in tempstr:
                            pass
                        else:
                            hotendfinal.append ( hotendline )    #gets extrusion information
    #Broken in current state and not in use
    def extrude ( call_file, lineorlayer, line_start, line_end, fileorraw ):
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
            pastline = [ 0, 0 ]
            nextline = [ 0, 0 ]
            tempE = tempF = 0
            for i in range ( 0, line_end + 1 ):
                tempstr = gcode.readline ()
                if i in range ( line_start, line_end + 1 ):
                    if "G1" in tempstr:
                        if "E" in tempstr and "F" in tempstr:
                            tempE = tempstr [ ( tempstr.find ( "E" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                            if ";" in tempstr:
                                tempF = tempstr [ ( tempstr.find ( "F" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
                            else:
                                tempF = tempstr [ ( tempstr.find ( "F" ) +1 ) : ( len ( tempstr ) + 2 ) ]
                        elif "E" in tempstr:
                            if ";" in tempstr:
                                tempE = tempstr [ ( tempstr.find ( "E" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
                            else:
                                tempE = tempstr [ ( tempstr.find ( "E" ) +1 ) : ( len ( tempstr ) + 2 ) ]
                        elif "F" in tempstr:
                            if ";" in tempstr:
                                tempF = tempstr [ ( tempstr.find ( "F" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
                            else:
                                tempF = tempstr [ ( tempstr.find ( "F" ) +1 ) : ( len ( tempstr ) + 2 ) ]
                    nextline [ 0 ] = float ( tempE )
                    if tempF != 0:
                        nextline [ 1 ] = float ( tempF )
                    else:
                        nextline [ 1 ] = pastline [ 1 ]
                    pastline [ 0 ] = nextline [ 0 ]
                    pastline [ 1 ] = nextline [ 1 ]
                    tempE = tempF = 0
                    lineextrude = { 'E' : nextline [ 0 ] * importape.filamentdiameter () * pi, 'F' : nextline [ 1 ] * importape.filamentdiameter () * pi }
                if 'X' in tempstr or 'Y' in tempstr or 'Z' in tempstr or 'E' in tempstr:
                    toolpathextrude.append ( lineextrude )
                else:
                    pass
            i = 0
            if fileorraw == 'raw':
                return ( toolpathextrude )
            else:
                return ( toolpathextrude )
                    
    #deconvolves hot bed and heated chamber information
    #returns dictionary
    def hotbed ( call_file, lineorlayer, line_start, line_end, initialize, fileorraw ):
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
            p = 0
            pastbed = [ 0, 0 ]
            nextbed = [ 0, 0 ]
            hotbedline = { 'HB' : 0, 'HC' : 0 }
            hotbedfinal = [ ]
            temphb = temphc = 0
            if initialize == 'yes':
                line_end = 100
            for i in range ( 0, line_start ):
                gcode.readline ()
                i = i + 1
            i = 0
            for i in range ( 0, line_end + 1 ):
                tempstr = gcode.readline ()
                if i in range ( line_start, line_end + 1 ):
                    if "M140" in tempstr:
                        if "S" in tempstr:
                            if ";" in tempstr:
                                temphb = tempstr [ ( tempstr.find ( "S" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
                            else:
                                temphb = tempstr [ ( tempstr.find ( "S" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                        else:
                            temphb = 0
                    if "M141" in tempstr:
                        if "S" in tempstr:
                            if ";" in tempstr:
                                temphc = tempstr [ ( tempstr.find ( "S" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
                            else:
                                temphc = tempstr [ ( tempstr.find ( "S" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                        else:
                            temphc = 0
                    if pastbed [ 0 ] != temphb:
                        nextbed [ 0 ] = temphb
                    if pastbed [ 1 ] != temphc:
                        nextbed [ 1 ] = temphc
                    p = 0
                    for p in range ( 0, 1):
                        pastbed [ p ] == nextbed [ p ]
                    hotbedline = { 'HB' : nextbed [ 0 ], 'HC' : nextbed [ 1 ] }
                    if initialize == 'yes':
                        if 'X' in tempstr or 'Y' in tempstr or 'Z' in tempstr:
                            pass
                        else:
                            hotbedfinal.append ( hotbedline )
                    elif 'X' in tempstr or 'Y' in tempstr or 'Z' in tempstr:
                        hotbedfinal.append ( hotbedline )
                    else:
                        pass
            i = 0
            if fileorraw == 'raw':
                return ( hotbedfinal )
            else:
                return ( hotbedfinal )
            
    #calles hotend and loads initialized perameters
    def hotendUI ( self, initialize ):
        return ( getape.hotend ( self.call_file, self.lineorlayer, self.line_start, self.line_end, initialize, self.fileorraw ) )
        
    #calles hotbed and loads initialized perameters
    def hotbedUI ( self, initialize ):
        return ( getape.hotbed ( self.call_file, self.lineorlayer, self.line_start, self.line_end, initialize, self.fileorraw ) )
        
    def pointUI ( self ):
        return ( getape.point ( self.call_file, self.implicitorexplicitaxes, self.implicitorexplicittravel, self.lineorlayer, self.line_start, self.line_end, self.fileorraw ) )

    def extrudeUI ( self ):
        return ( getape.extrude ( self.call_file, self.lineorlayer, self.line_start, self.line_end, self.fileorraw ) )
    
print ( getape ( 'auto' ).hotendUI ( 'yes' ) )
print ( getape ( 'auto' ).hotbedUI ( 'yes' ) )
print ( getape ( 'auto' ).pointUI ( ) )
print ( getape ( 'auto' ).extrudeUI ( ) )