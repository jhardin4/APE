#screws up on retraction and z-hop  this NEEDS fixed
#must get velocity data from getape.extrude  once done, highly complex infill (fabrics included) will work

import threading, os, linecache
from UI.import_ape import importape
from UI.run_ape import runape

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
        self.UI_line = importape.config ( 'UI_line' )
        #used for selecting file path behavior of getape.xxx
        if call_file == 'auto':
            self.call_file = runape ( '%s/Print_With_APE/*.gcode' % ( os.path.expanduser ( '~' ) ) ).findfile ( 'file' )
        else:
            self.call_file = call_file
#        self.thread_number = importape.getthreadcount
    
    #used in this manner so that threading can be implimented for decreasing processing time later
    def run ( self ):
        pass
    #deconvolves spatial points
    #returns dictionary
    def point ( call_file, implicitorexplicitaxes, implicitorexplicittravel,  lineorlayer, line_start, line_end, UI_line, past_line ):
        if lineorlayer == 'layer':
            templine_start = importape.layertoline ( call_file, 'start', line_start, line_end )
            templine_end = importape.layertoline ( call_file, 'end', line_start, line_end )
            line_start = templine_start
            line_end = templine_end
        if line_start == 'start':
            line_start = importape.numberoflines ( call_file, 'start' )
        if line_end == 'end':
            line_end = importape.numberoflines ( call_file, 'end' )
        pastpoint  = [ 0, 0, 0 ]
        if past_line != 'Empty':
            pastpoint = [ past_line.get ( 'X' ), past_line.get ( 'Y' ), past_line.get ( 'Z' ) ]
        nextpoint = [ 0, 0, 0 ]
        toolpathpoint = [ { 'Empty' : 'Empty' } ]
        linepoint = { 'X' : 0, 'Y' : 0, 'Z' : 0 }
        tempX = tempY = tempZ = 0
        i = 0
        for i in range ( line_start, line_end + 1 ):
            if line_start == ( line_end ):
                tempstr = linecache.getline ( call_file, line_start )
            else:
                tempstr = linecache.getline ( call_file, i )
            if len ( tempstr ) != 0:
                if tempstr [ 0 ] != ';':
                    if "G1" in tempstr:
                        if "X" in tempstr and "Y" in tempstr and "Z" in tempstr:
                            tempX = tempstr [ ( tempstr.find ( "X" ) + 1 ) : ( tempstr.find ( "Y" ) - tempstr.find ( "X" ) - 1 + tempstr.find ( "X" ) ) ]
                            tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( tempstr.find ( "Z" ) - tempstr.find ( "Y" ) - 1 + tempstr.find ( "Y" ) ) ]
                            if "E" in tempstr:
                                tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "E" ) - 1 ) ]
                            elif "F" in tempstr:
                                tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                            else:
                                if ";" in tempstr:
                                    tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
                                else:
                                    tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                        elif "X" in tempstr and "Y" in tempstr:
                            tempX = tempstr [ ( tempstr.find ( "X" ) + 1 ) : ( tempstr.find ( "Y" ) - tempstr.find ( "X" ) - 1 + tempstr.find ( "X" ) ) ]
                            if "E" in tempstr:
                                tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( tempstr.find ( "E" ) - 1 ) ]
                            elif "F" in tempstr:
                                tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                            else:
                                if ";" in tempstr:
                                    tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
                                else:
                                    tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                        elif "X" in tempstr and "Z" in tempstr:
                            tempX = tempstr [ ( tempstr.find ( "X" ) + 1 ) : ( tempstr.find ( "Y" ) - tempstr.find ( "X" ) - 1 + tempstr.find ( "X" ) ) ]
                            if "E" in tempstr:
                                tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "E" ) - 1 ) ]
                            elif "F" in tempstr:
                                tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                            else:
                                if ";" in tempstr:
                                    tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
                                else:
                                    tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                        elif "Y" in tempstr and "Z" in tempstr:
                            tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( tempstr.find ( "Z" ) - tempstr.find ( "Y" ) - 1 + tempstr.find ( "Y" ) ) ]
                            if "E" in tempstr:
                                tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "E" ) - 1 ) ]
                            elif "F" in tempstr:
                                tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                            else:
                                if ";" in tempstr:
                                    tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
                                else:
                                    tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                        elif "X" in tempstr:
                            if "E" in tempstr:
                                tempX = tempstr [ ( tempstr.find ( "X" ) + 1 ) : ( tempstr.find ( "E" ) - 1 ) ]
                            elif "F" in tempstr:
                                tempX = tempstr [ ( tempstr.find ( "X" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                            else:
                                if ";" in tempstr:
                                    tempX = tempstr [ ( tempstr.find ( "X" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
                                else:
                                    tempX = tempstr [ ( tempstr.find ( "X" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                        elif "Y" in tempstr:
                            if "E" in tempstr:
                                tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( tempstr.find ( "E" ) - 1 ) ]
                            elif "F" in tempstr:
                                tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                            else:
                                if ";" in tempstr:
                                    tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
                                else:
                                    tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                        elif "Z" in tempstr:
                            if "E" in tempstr:
                                tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "E" ) - 1 ) ]
                            elif "F" in tempstr:
                                tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                            else:
                                if ";" in tempstr:
                                    tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
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
                elif UI_line == 'yes':
                    if "G1" in tempstr:
                        toolpathpoint.append ( linepoint )
                    else:
                        toolpathpoint.append ( { 'Empty' : 'Empty' } )
                elif UI_line == 'no':
                    toolpathpoint.append ( linepoint )
                else:
                    pass
        return ( toolpathpoint )
    
    #deconvolves hotend heat, system fan, bridging fan, tool change, tool #, multiplexer #, multiplexer change, and tool change distance information
    #when a tool change occours:
        #it will determine if a multiplexer is used or not via 'auto' stored in tempmxa
        #if there is no multiplexer, it will look for a user change and store 'usr change' in tempmxa
        #lastly it will not change tempmxa and returns ''.  here there are assumed to be multiple tool heads
        #for M701 it returns a chnage in MX if a multiplexer is present, eleswise it returns a change in T
        #M701 returns load in TC
        #M702 is the same as M701 but returns unload in TC
        #T0-T4 return 0-4 in MX 
            #if mxa is not auto, but mx changes from 0 to another number, a multiplexer will be assumed and mxa will be set to auto
    #doesnot wait for temperature changes to occour
    #returns dictionary
    def hotend ( call_file, lineorlayer, line_start, line_end, initialize, UI_line, past_line ):
        if lineorlayer == 'layer':
            templine_start = importape.layertoline ( call_file, 'start', line_start, line_end )
            templine_end = importape.layertoline ( call_file, 'end', line_start, line_end )
            line_start = templine_start
            line_end = templine_end
        if line_start == 'start':
            line_start = importape.numberoflines ( call_file, 'start' )
        if line_end == 'end':
            line_end = importape.numberoflines ( call_file, 'end' )
        i = 0
        p = 0
        pastline = [ 0, 0, 0, '', 1, 1, '', 0 ]
        if past_line != 'Empty':
            pastline = [ past_line.get ( 'H' ), past_line.get ( 'SF' ), past_line.get ( 'BF' ), past_line.get ( 'TC' ), past_line.get ( 'T' ), past_line.get ( 'MX' ), past_line.get ( 'MXA' ), past_line.get ( 'D' ) ]
        nextline = [ 0, 0, 0, '', 1, 1, '', 0 ]
        hotendline = { 'H' : 0, 'SF' : 0, 'BF' : 0, 'TC' : '', 'T' : 1, 'MX' : 1, 'MXA' : '', 'D' : 0 }
        hotendfinal = [ { 'Empty' : 'Empty' } ]
        temph = tempfan = tempsf = tempbf = temptmx = tempt = tempmx = tempd = 0
        temptc = tempmxa = ''
        if initialize == 'yes':
            line_start = 0
            line_end = 100
        for i in range ( line_start, line_end + 1 ):
            if line_start == line_end:
                tempstr = linecache.getline (call_file, line_start )
            else:
                tempstr = linecache.getline (call_file, line_start )
            if len ( tempstr ) != 0:
                if tempstr [ 0 ] != ';':
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
                        elif "M702" in tempstr:
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
                                tempmx = -1 * ( temptmx + 10 )
                            else:
                                tempt = -1 * ( temptmx + 10 )
                            temptc = 'unload'
                        elif "T0" in tempstr:
                            tempmx = 0
                            tempmxa == 'AUTO'
                        elif "T1" in tempstr:
                            tempmx = 1
                            tempmxa == 'AUTO'
                        elif "T2" in tempstr:
                            tempmx = 2
                            tempmxa == 'AUTO'
                        elif "T3" in tempstr:
                            tempmx = 3
                            tempmxa == 'AUTO'
                        elif "T4" in tempstr:
                            tempmx = 4
                            tempmxa == 'AUTO'
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
                elif UI_line == 'yes':
                    if "M104" in tempstr or "M106" in tempstr or "M107" in tempstr or "M109" in tempstr or "M600" in tempstr or "M701" in tempstr or "M702" in tempstr or "T0" in tempstr or "T1" in tempstr or "T2" in tempstr or "T3" in tempstr or "T4" in tempstr:
                        hotendfinal.append ( hotendline )
                    else:
                        hotendfinal.append ( { 'Empty' : 'Empty' } )
                elif UI_line == 'no':
                    hotendfinal.append ( hotendline )    #gets extrusion information
                else:
                    pass
        if initialize == 'yes':    
            return ( hotendfinal [ -1 ] )
        else:
            return ( hotendfinal )
    #Broken in current state and not in use
    def extrude ( call_file, lineorlayer, line_start, line_end, UI_line, past_line ):
        if lineorlayer == 'layer':
            templine_start = importape.layertoline ( call_file, 'start', line_start, line_end )
            templine_end = importape.layertoline ( call_file, 'end', line_start, line_end )
            line_start = templine_start
            line_end = templine_end
        if line_start == 'start':
            line_start = importape.numberoflines ( call_file, 'start' )
        if line_end == 'end':
            line_end = importape.numberoflines ( call_file, 'end' )
        i = 0
        toolpathextrude = [ { 'Empty' : 'Empty' } ]
        pastline = [ 0, 0, 'Empty' ]
        if past_line != 'Empty':
            pastline = [ past_line.get ( 'E' ), past_line.get ( 'F' ), past_line.get ( 'SetE' ) ]
        nextline = [ 0, 0, 'Empty' ]
        tempE = tempF = 0
        tempsetE = 'Empty'
        for i in range ( line_start, line_end + 1 ):
            if line_start == line_end:
                tempstr = linecache.getline (call_file, line_start )
            else:
                tempstr = linecache.getline (call_file, line_start )
            if len ( tempstr ) != 0:
                if tempstr [ 0 ] != ';':
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
                        if "G92" in tempstr:
                            if "E" in tempstr:
                                if ";" in tempstr:
                                    tempsetE = tempstr [ ( tempstr.find ( "E" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
                                else:
                                    tempsetE = tempstr [ ( tempstr.find ( "E" ) +1 ) : ( len ( tempstr ) + 2 ) ]
                nextline [ 0 ] = float ( tempE )
                if tempF != 0:
                    nextline [ 1 ] = float ( tempF )
                else:
                    nextline [ 1 ] = pastline [ 1 ]
                if tempsetE != 'Empty':
                    nextline [ 2 ] = float ( tempsetE )
                tempsetE = 'Empty'
                pastline [ 0 ] = nextline [ 0 ]
                pastline [ 1 ] = nextline [ 1 ]
                pastline [ 2 ] = nextline [ 2 ]
                tempE = tempF = 0
                lineextrude = { 'E' : nextline [ 0 ], 'F' : nextline [ 1 ], 'SetE' : nextline [ 2 ] }
            if 'X' in tempstr or 'Y' in tempstr or 'Z' in tempstr or 'E' in tempstr:
                toolpathextrude.append ( lineextrude )
            elif UI_line == 'yes':
                if "G1" in tempstr or "G92" in tempstr:
                    toolpathextrude.append ( lineextrude )
                else:
                    toolpathextrude.append ( { 'Empty' : 'Empty' } )
            elif UI_line == 'no':
                toolpathextrude.append ( lineextrude )
            else:
                pass
        return ( toolpathextrude )
                    
    #deconvolves hot bed and heated chamber information
    #returns dictionary
    def hotbed ( call_file, lineorlayer, line_start, line_end, initialize, UI_line, past_line ):
        if lineorlayer == 'layer':
            templine_start = importape.layertoline ( call_file, 'start', line_start, line_end )
            templine_end = importape.layertoline ( call_file, 'end', line_start, line_end )
            line_start = templine_start
            line_end = templine_end
        if line_start == 'start':
            line_start = importape.numberoflines ( call_file, 'start' )
        if line_end == 'end':
            line_end = importape.numberoflines ( call_file, 'end' )
        i = 0
        p = 0
        pastbed = [ 0, 0 ]
        if past_line != 'Empty':
            pastbed = [ past_line.get ( 'HB' ), past_line.get ( 'HC' ) ]
        nextbed = [ 0, 0 ]
        hotbedline = { 'HB' : 0, 'HC' : 0 }
        hotbedfinal = [ { 'Empty' : 'Empty' } ]
        temphb = 0
        temphc = -1
        if initialize == 'yes':
            line_start = 0
            line_end = 100
        for i in range ( line_start, line_end + 1 ):
            if line_start == line_end:
                tempstr = linecache.getline (call_file, line_start )
            else:
                tempstr = linecache.getline (call_file, line_start )
            if len ( tempstr ) != 0:
                if tempstr [ 0 ] != ';':
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
                elif UI_line == 'yes':
                    if "M140" in tempstr or "M141" in tempstr:
                        hotbedfinal.append ( hotbedline )
                    else:
                        hotbedfinal.append ( { 'Empty' : 'Empty' } )
                elif UI_line == 'no':
                    hotbedfinal.append ( hotbedline )
                else:
                    pass
        if initialize == 'yes':
            return ( hotbedfinal [ -1 ] )
        else:
            return ( hotbedfinal )
            
    def interpoint ( call_file, implicitorexplicitaxes, implicitorexplicittravel,  lineorlayer, line_start, line_end, UI_line, past_line ):
        if lineorlayer == 'layer':
            templine_start = importape.layertoline ( call_file, 'start', line_start, line_end )
            templine_end = importape.layertoline ( call_file, 'end', line_start, line_end )
            line_start = templine_start
            line_end = templine_end
        if line_start == 'start':
            line_start = importape.numberoflines ( call_file, 'start' )
        if line_end == 'end':
            line_end = importape.numberoflines ( call_file, 'end' )
        pastpoint  = nextpoint = [ 'Empty', 'Empty', 'Empty', 'Empty', 'Empty', 'Empty' ]
        if past_line != 'Empty':
            pastpoint = [ past_line.get ( 'X' ), past_line.get ( 'Y' ), past_line.get ( 'Z' ), past_line.get ( 'E' ), past_line.get ( 'F' ), past_line.get ( 'SetE' ) ]
            #print ( pastpoint )
        toolpathpoint = [ { 'Empty' : 'Empty' } ]
        linepoint = { 'X' : 0, 'Y' : 0, 'Z' : 0, 'E' : 0, 'F' : 0, 'SetE' : 'Empty' }
        tempX = tempY = tempZ = tempE = tempF = 'Empty'
        tempsetE = 'Empty'
        i = 0
        for i in range ( line_start, line_end + 1 ):
            if line_start == line_end:
                tempstr = linecache.getline (call_file, line_start )
            else:
                tempstr = linecache.getline (call_file, line_start )
            if len ( tempstr ) != 0:
                if tempstr [ 0 ] != ';':
                    if "G1" in tempstr:
                        if "X" in tempstr and "Y" in tempstr and "Z" in tempstr:
                            tempX = tempstr [ ( tempstr.find ( "X" ) + 1 ) : ( tempstr.find ( "Y" ) - tempstr.find ( "X" ) - 1 + tempstr.find ( "X" ) ) ]
                            tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( tempstr.find ( "Z" ) - tempstr.find ( "Y" ) - 1 + tempstr.find ( "Y" ) ) ]
                            if "E" in tempstr:
                                tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "E" ) - 1 ) ]
                            elif "F" in tempstr:
                                tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                            else:
                                if ";" in tempstr:
                                    tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
                                else:
                                    tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                        elif "X" in tempstr and "Y" in tempstr:
                            tempX = tempstr [ ( tempstr.find ( "X" ) + 1 ) : ( tempstr.find ( "Y" ) - tempstr.find ( "X" ) - 1 + tempstr.find ( "X" ) ) ]
                            if "E" in tempstr:
                                tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( tempstr.find ( "E" ) - 1 ) ]
                            elif "F" in tempstr:
                                tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                            else:
                                if ";" in tempstr:
                                    tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
                                else:
                                    tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                        elif "X" in tempstr and "Z" in tempstr:
                            tempX = tempstr [ ( tempstr.find ( "X" ) + 1 ) : ( tempstr.find ( "Y" ) - tempstr.find ( "X" ) - 1 + tempstr.find ( "X" ) ) ]
                            if "E" in tempstr:
                                tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "E" ) - 1 ) ]
                            elif "F" in tempstr:
                                tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                            else:
                                if ";" in tempstr:
                                    tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
                                else:
                                    tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                        elif "Y" in tempstr and "Z" in tempstr:
                            tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( tempstr.find ( "Z" ) - tempstr.find ( "Y" ) - 1 + tempstr.find ( "Y" ) ) ]
                            if "E" in tempstr:
                                tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "E" ) - 1 ) ]
                            elif "F" in tempstr:
                                tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                            else:
                                if ";" in tempstr:
                                    tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
                                else:
                                    tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                        elif "X" in tempstr:
                            if "E" in tempstr:
                                tempX = tempstr [ ( tempstr.find ( "X" ) + 1 ) : ( tempstr.find ( "E" ) - 1 ) ]
                            elif "F" in tempstr:
                                tempX = tempstr [ ( tempstr.find ( "X" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                            else:
                                if ";" in tempstr:
                                    tempX = tempstr [ ( tempstr.find ( "X" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
                                else:
                                    tempX = tempstr [ ( tempstr.find ( "X" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                        elif "Y" in tempstr:
                            if "E" in tempstr:
                                tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( tempstr.find ( "E" ) - 1 ) ]
                            elif "F" in tempstr:
                                tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                            else:
                                if ";" in tempstr:
                                    tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
                                else:
                                    tempY = tempstr [ ( tempstr.find ( "Y" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
                        elif "Z" in tempstr:
                            if "E" in tempstr:
                                tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "E" ) - 1 ) ]
                            elif "F" in tempstr:
                                tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( "F" ) - 1 ) ]
                            else:
                                if ";" in tempstr:
                                    tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
                                else:
                                    tempZ = tempstr [ ( tempstr.find ( "Z" ) + 1 ) : ( len ( tempstr ) + 2 ) ]
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
                        if "G92" in tempstr:
                            if "E" in tempstr:
                                if ";" in tempstr:
                                    tempsetE = tempstr [ ( tempstr.find ( "E" ) + 1 ) : ( tempstr.find ( ";" ) - 1 ) ]
                                else:
                                    tempsetE = tempstr [ ( tempstr.find ( "E" ) +1 ) : ( len ( tempstr ) + 2 ) ]    
                
            if implicitorexplicitaxes == 'implicit':
                nextpoint [ 0 ] = pastpoint [ 0 ] + float ( tempX )
                nextpoint [ 1 ] = pastpoint [ 1 ] + float ( tempY )
                nextpoint [ 2 ] = pastpoint [ 2 ] + float ( tempZ )
                nextpoint [ 3 ] = float ( tempE )
                nextpoint [ 4 ] = float ( tempF )
                if tempsetE != 'Empty':
                    nextpoint [ 5 ] = float ( tempsetE )
                tempsetE = 'Empty'
                pastpoint[ 0 ] = nextpoint[ 0 ]
                pastpoint[ 1 ] = nextpoint[ 1 ]
                pastpoint[ 2 ] = nextpoint[ 2 ]
            if implicitorexplicitaxes == 'explicit':
                if tempX != 'Empty':
                    nextpoint [ 0 ] = float ( tempX )
                else:
                    nextpoint [ 0 ] = pastpoint [ 0 ]
                if tempY != 'Empty':
                    nextpoint [ 1 ] = float ( tempY )
                else:
                    nextpoint [ 1 ] = pastpoint [ 1 ]
                #print ( tempZ )
                #print ( nextpoint [ 2 ] )
                if tempZ != 'Empty':
                    nextpoint [ 2 ] = float ( tempZ )
                else:
                    nextpoint [ 2 ] = pastpoint [ 2 ]
                #print ( pastpoint )
                #print ( nextpoint [ 2 ] )
                if tempE != 'Empty':
                    nextpoint [ 3 ] = float ( tempE )
                else:
                    nextpoint [ 3 ] = pastpoint [ 3 ]
                if tempF != 'Empty':
                    nextpoint [ 4 ] = float ( tempF )
                else:
                    nextpoint [ 4 ] = pastpoint [ 4 ]
                if tempsetE != 'Empty':
                    nextpoint [ 5 ] = float ( tempsetE )
                tempsetE = 'Empty'
            linepoint = { 'X' : nextpoint [ 0 ], 'Y' : nextpoint [ 1 ], 'Z' : nextpoint [ 2 ], 'E' : nextpoint [ 3 ], 'F' : nextpoint [ 4 ], 'SetE' : nextpoint [ 5 ] }
            if i in range ( line_start, line_end + 1 ):
                if 'X' in tempstr or 'Y' in tempstr or 'Z' in tempstr:
                    toolpathpoint.append ( linepoint )
                elif UI_line == 'yes':
                    if "G1" in tempstr or "G92" in tempstr:
                        toolpathpoint.append ( linepoint )
                    else:
                        toolpathpoint.append ( { 'Empty' : 'Empty' } )
                elif UI_line == 'no':
                    toolpathpoint.append ( linepoint )
                else:
                    pass
        return ( toolpathpoint )            
            
    #calles hotend and loads initialized perameters
    def hotendUI ( self, initialize, past_line ):
        return ( getape.hotend ( self.call_file, self.lineorlayer, self.line_start, self.line_end, initialize, self.UI_line, past_line ) )
    
    def hotendUI_line ( self, line, past_line ):
        line_start = line
        line_end = line
        return ( getape.hotend ( self.call_file, self.lineorlayer, line_start, line_end, 'no', 'yes', past_line ) [ -1 ] )    
    
    #calles hotbed and loads initialized perameters
    def hotbedUI ( self, initialize, past_line ):
        return ( getape.hotbed ( self.call_file, self.lineorlayer, self.line_start, self.line_end, initialize, self.UI_line, past_line ) )
        
    def hotbedUI_line ( self, line, past_line ):
        line_start = line
        line_end = line
        return ( getape.hotbed ( self.call_file, self.lineorlayer, line_start, line_end, 'no', 'yes', past_line ) [ -1 ] )
    
    def pointUI ( self, past_line ):
        return ( getape.point ( self.call_file, self.implicitorexplicitaxes, self.implicitorexplicittravel, self.lineorlayer, self.line_start, self.line_end, self.UI_line, past_line ) )
    
    def pointUI_line ( self, line, past_line ):
        line_start = line
        line_end = line
        return ( getape.point ( self.call_file, self.implicitorexplicitaxes, self.implicitorexplicittravel, self.lineorlayer, line_start, line_end, 'yes', past_line ) [ -1 ] )
    
    def interpointUI ( self, past_line ):
        return ( getape.interpoint ( self.call_file, self.implicitorexplicitaxes, self.implicitorexplicittravel, self.lineorlayer, self.line_start, self.line_end, self.UI_line, past_line ) )

    def interpointUI_line ( self , line, past_line ):
        line_start = line
        line_end = line
        return ( getape.interpoint ( self.call_file, self.implicitorexplicitaxes, self.implicitorexplicittravel, self.lineorlayer, line_start, line_end, 'yes', past_line ) [ -1 ] )

    def extrudeUI ( self, past_line ):
        return ( getape.extrude ( self.call_file, self.lineorlayer, self.line_start, self.line_end, self.UI_line, past_line ) )
    
    def extrudeUI_line ( self, line, past_line ):
        line_start = line
        line_end = line
        return ( getape.extrude ( self.call_file, self.lineorlayer, line_start, line_end, 'yes', past_line ) [ -1 ] )


#print ( getape ( 'auto' ).hotendUI ( 'yes' ) )
#print ( getape ( 'auto' ).hotbedUI ( 'yes' ) )
#print ( getape ( 'auto' ).pointUI_line ( 1, 'Empty' ) )
#print ( getape ( 'auto' ).pointUI ( ) )
#print ( getape ( 'auto' ).interpointUI ( 'Empty' ) )
#print ( getape ( 'auto' ).extrudeUI ( ) )