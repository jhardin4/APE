"""
@author: Nicholas Arn
contact for questions that the comments cannot answer
"""
import os
import run_ape
import import_ape
import deconvolver

def interlace ( fileorlayer, wholeorpointcloud, usememory ):
    if fileorlayer == 'file':
        line_start = 0
        line_end = import_ape.importape.numberoflines ( run_ape.runape ( '%s/Print_With_APE/*.gcode' % ( os.path.expanduser ( '~' ) ) ).findfile ( 'file' ), 'end' )
        #line_end = 100
    #WIP!!!!!!!!!!!!!!!!
    #for use when AI needs to easily modify print perameters layer by layer
    #not yet priority
    elif fileorlayer == 'layer':
        pass
    else:
        print ( 'must specify "file" or "layer"' )
    interlace = []
    tempb = {}
    tempt = {}
    tempp = {}
    pasttempb = pasttempt = pasttempp = {}
    for i in range ( line_start, line_end ):
        #print ( i )
        tempb = deconvolver.getape ( 'auto' ).hotendUI_line ( i )
        #print ( tempb )
        #tempt = deconvolver.getape ( 'auto' ).hotbedUI_line ( i )
        #tempp = deconvolver.getape ( 'auto' ).interpointUI_line ( i )
        #print ( tempb.items ( ) )
        if pasttempb.items ( ) != tempb.items ( ):
            interlace.append ( tempb )
        #elif pasttempt != tempt:
            #interlace.append ( tempt )
        #elif pasttempp != tempp:
            #interlace.append ( tempp )
        
        pasttempb = tempb
        pasttempt = tempt
        pasttempp = tempp
    print ( interlace )
        
        
        
interlace ( 'file', 'whole', 'yes' )