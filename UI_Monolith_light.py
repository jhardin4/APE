'''
This file is an example of how to interact with APE as a single-process
application.
'''
import time, os
#import Core
#import Procedures
#from AppTemplates.FlexPrinterMonolith import FlexPrinterMonolith as AppBuilder
import UI.run_ape as run_ape
import UI.start_ape as start_ape
import UI.line_interlacer as line_interlace
import UI.import_ape as import_ape


def Auto_Run_Monolith ( ):
    convert_1 = convert_2 = sendcode = [ ]
    convert_1 = convert_2 = line_interlace.interlace ( 'file', 'whole', 'yes' )
    for i in range ( 0, len ( convert_1 ) ):
        tempCon = convert_1 [ i ]
        if len ( tempCon ) == 2:
            hotbed = hot_bed ( tempCon.get ( 'HB' ), tempCon.get ( 'HC' ) )
            sendcode = sendcode + hotbed
            #print ( hotbed )
            #print ( 'line :', i )
            
        elif len ( tempCon ) == 8:
            hotend = hot_end ( tempCon.get ( 'H' ), tempCon.get ( 'SF' ), tempCon.get ( 'BF' ), tempCon.get ( 'TC' ), tempCon.get ( 'T' ), tempCon.get ( 'MX' ), tempCon.get ( 'MXA' ), tempCon.get ( 'D' ) )
            sendcode = sendcode + hotend
            #print ( hotend )
            #print ( 'line :', i)
            
        elif len ( tempCon ) == 6:
            toolandpath = extrude_path ( tempCon.get ( 'X' ), tempCon.get ( 'Y' ), tempCon.get ( 'Z' ), tempCon.get ( 'E' ), tempCon.get ( 'F' ), tempCon.get ( 'SetE' ) )
            sendcode = sendcode + toolandpath
            #print ( toolandpath )
            #print ( 'line :', i)
            
        else:
            print ( 'fatal line_interlacer error, tempCon has length : %s' % ( len ( tempCon ) ), ', on line : %s' % ( i ) )
    #print ( sendcode )
    
    
    """
    connect, send code 1 line at a time with a que of 3 total.
    log events here as code is sent. log using convert_1 or convert_2 as coorisponding gcode is sent.
    """
    
    
    
    
    
    
    #print ( convert_1 )
    
def hot_bed ( hot_bed_heat, hot_chamber ):
    nextcommand = [ ]
    nextcommand.append ('M140 S%s' % ( hot_bed_heat ) )
    if hot_chamber != -1:
        nextcommand.append ('M141 S%s' % ( hot_chamber ) )
    return ( nextcommand )

def hot_end ( hot_end_heat, hot_end_fan, bridge_fan, tool_change, tool_number, multiplexer_number, multiplexer_change, tool_change_distance ):
    nextcommand = [ ]
    nextcommand.append ('M104 S%s' % ( hot_end_heat ) )
    nextcommand.append ( 'M106 P1 S%s' % ( bridge_fan ) + ' P2 S%s' % ( hot_end_fan ) )
    if tool_change == 'USR Load':
        nextcommand.append ( 'M600 Z25' )
    elif tool_change == '':
        if multiplexer_change == '':
            if tool_number < 0:
                tool_number_temp = -1* ( tool_number - 10 )
                if tool_change_distance != 0:
                    nextcommand.append ( 'M702 T%s' % ( tool_number_temp ) + ' L%s' % ( tool_change_distance ) )
                elif tool_change_distance == 0:
                    nextcommand.append ( 'M702 T%s' % ( tool_number_temp ) )
                else:
                    nextcommand.append ( 'M702 T%s' % ( tool_number_temp ) )
            elif tool_number >= 0:
                if tool_change_distance != 0:
                    nextcommand.append = ( 'M701 T%s' % ( tool_number ) + ' L%s' % ( tool_change_distance ) )
                elif tool_change_distance == 0:
                    nextcommand.append ( 'M701 T%s' % ( tool_number ) )
                else:
                    nextcommand.append ( 'M701 T%s' % ( tool_number ) )
        elif multiplexer_change == 'AUTO':
            nextcommand.append ('T%s' % ( multiplexer_number ) )
    return ( nextcommand )
    
def extrude ( extrude_distance, extrude_velocity, set_new_extrude_distance ):
    nextcommand = [ ]
    if set_new_extrude_distance != 'Empty':
        nextcommand.append ( 'G92 E%s' % ( set_new_extrude_distance ) )
    nextcommand.append ( 'G1 F%s' % ( extrude_velocity ) )
    return ( nextcommand )
        
def extrude_path ( x_point, y_point, z_point, extrude_distance, extrude_velocity, set_new_extrude_distance ):
    nextcommand = [ ]
    if set_new_extrude_distance != 'Empty':
        nextcommand.append ( 'G92 E%s' % ( set_new_extrude_distance ) )
    nextcommand.append ( 'G1 F%s' % ( extrude_velocity ) )
    nextcommand.append ( 'G1 X%s' % ( x_point ) + ' Y%s' % ( y_point ) + ' Z%s' % ( z_point ) + ' E%s' % ( extrude_distance ) )
    return ( nextcommand )

Auto_Run_Monolith ( )

sa = start_ape.startape ( )
start = 0
if start == 'start':
    if sa.checksfile ( ) == 'ready 1':
        ra = run_ape.runape ( '%s/Print_With_APE/*.gcode' % ( os.path.expanduser ( '~' ) ) )
        while ra.running:
            try:
                time.sleep ( 1 )
                if ra.watchfolder ( ) == 'execute':
                    #print ( 'execute stage 2' )
                    Auto_Run_Monolith ( )
            except FileNotFoundError:
                print ( ' file not found ' )
            except None:
                None
            except:
                print ( ' unknown error ' )
            #print ( ra.runinback ( ) )
            if ra.runinback == 'execute':
                Auto_Run_Monolith ( )
                #print ( 'execute stage 3' )
            else:
                time.sleep ( 1 )
    
    elif sa.checksfile ( ) == 'ready 0':
        sa.installape ( )
        ra = run_ape.runape ( '%s/Print_With_APE/*.gcode' % ( os.path.expanduser ( '~' ) ) )
        while ra.running:
            try:
                time.sleep ( 1 )
                if ra.watchfolder ( ) == 'execute':
                    #print ( 'execute stage 2' )
                    Auto_Run_Monolith ( )
            except FileNotFoundError:
                print ( ' file not found ' )
            except None:
                None
            except:
                print ( ' unknown error ' )
            #print ( ra.runinback ( ) )
            if ra.runinback == 'execute':
                Auto_Run_Monolith ( )
                #print ( 'execute stage 3' )
            else:
                time.sleep ( 1 )
    
    elif sa.checksfile ( ) == 'fatal error':
        print ( sa.checksfile ( ) )