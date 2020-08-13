'''
This file is an example of how to interact with APE as a single-process
application.
'''
import time, os
import Core
import Procedures
from AppTemplates.FlexPrinterMonolith import FlexPrinterMonolith as AppBuilder
import UI.run_ape as run_ape
import UI.start_ape as start_ape
import UI.line_interlacer as line_interlace
import UI.import_ape as import_ape


def Auto_Run_Monolith ( ):

    pass


sa = start_ape.startape ( )
#sa.test ()

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