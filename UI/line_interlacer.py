"""
@author: Nicholas Arn
contact for questions that the comments cannot answer
"""
import os
import UI.run_ape as run_ape
import UI.import_ape as import_ape
import UI.deconvolver as deconvolver

def interlace ( fileorlayer, wholeorpointcloud, usememory ):
    if fileorlayer == 'file':
        line_start = 0
        line_end = import_ape.importape.numberoflines ( run_ape.runape ( '%s/Print_With_APE/*.gcode' % ( os.path.expanduser ( '~' ) ) ).findfile ( 'file' ), 'end' )
        #line_end = 2500
        past_line_b = past_line_t = past_line_p = past_line_p2 = 'Empty'
    #WIP!!!!!!!!!!!!!!!!
    #for use when AI needs to easily modify print perameters layer by layer
    #not yet priority
    elif fileorlayer == 'layer':
        pass
    else:
        print ( 'must specify "file" or "layer"' )
    interlace = []
    pasttempb = tempb = pasttempt = tempt = pasttempp = tempp = pasttempp2 = tempp2 = {}
    for i in range ( line_start, line_end ):
        #print ( i )
        if wholeorpointcloud == 'whole' or wholeorpointcloud == 'whole pc':
            tempb = deconvolver.getape ( 'auto' ).hotendUI_line ( i, past_line_b )
            if tempb != { 'Empty' : 'Empty' }:
                past_line_b = tempb
            tempt = deconvolver.getape ( 'auto' ).hotbedUI_line ( i, past_line_t )
            if tempt != { 'Empty' : 'Empty' }:
                past_line_t = tempt
        if wholeorpointcloud == 'whole':
            tempp = deconvolver.getape ( 'auto' ).interpointUI_line ( i, past_line_p )
            #print ( 'TEMPP', tempp )
            #print ( 'PAST_LINE', past_line_p )
            if tempp != { 'Empty' : 'Empty' }:
                past_line_p = tempp
            #print ( 'NEW_PAST_LINE', past_line_p )
            #print ( '__________________________' )
        elif wholeorpointcloud == 'pointcloud' or wholeorpointcloud == 'whole pc':
            tempp2 = deconvolver.getape ( 'auto' ).pointUI_line ( i, past_line_p2 )
            if tempp2 != { 'Empty' : 'Empty' }:
                past_line_p2 = tempp2
        
        if wholeorpointcloud == 'whole' or wholeorpointcloud == 'whole pc':
            if pasttempb.items ( ) != tempb.items ( ):
                interlace.append ( past_line_b )
            elif pasttempt != tempt:
                interlace.append ( past_line_t )
        if wholeorpointcloud == 'whole':
            if pasttempp != tempp:
                interlace.append ( past_line_p )
        elif wholeorpointcloud == 'pointcloud' or wholeorpointcloud == 'whole pc':
            if pasttempp2 != tempp2:
                interlace.append ( past_line_p2 )
        
        if wholeorpointcloud == 'whole' or wholeorpointcloud == 'whole pc':
            pasttempb = tempb
            pasttempt = tempt
        if wholeorpointcloud == 'whole':
            pasttempp = tempp
        elif wholeorpointcloud == 'pointcloud' or wholeorpointcloud == 'whole pc':
            pasttempp2 = tempp2
    if usememory == 'yes':
        return ( interlace )
    elif usememory == 'no':
        pass #return a file to be called from later in the logs folder??
    else:
        pass
        
        
        
#print ( interlace ( 'file', 'whole', 'yes' ) )