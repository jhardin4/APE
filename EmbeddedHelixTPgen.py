from ToolPathGeneration import CompGeo as cg
from ToolPathGeneration import ToolPathTools as tpt
from ToolPathGeneration import HoneycombToolpathTools as htt
import math

def Make_TPGen_Data(dielectric, conductor):
    TPGen_Data={}
    
    TPGen_Data['conductorname'] = conductor
    TPGen_Data['dielectricname'] = dielectric
    
    
    TPGen_Data['helixindex_X'] = 5
    TPGen_Data['helixindex_Y'] = 3
    
    #Computational Geometry Tolerances
    TPGen_Data['disttol'] = 1E-12 #Distance tolerance
    TPGen_Data['angtol'] = 1E-7  #Angular tolerance
    
    #Base Hexagon Dimensions
    TPGen_Data['dima'] = 3.574 #side length
    TPGen_Data['dimb'] = TPGen_Data['dima'] * 3**0.5 #distance between opposite dima faces
    TPGen_Data['dimc'] = TPGen_Data['dima']/2 #height of top(bottom) triangle
    
    #Number of cells
    TPGen_Data['cellsX'] = 10
    TPGen_Data['cellsY'] = 8
    
    #Print parameters
    TPGen_Data['tiph'] = 0.8 #offset from printing surface
    TPGen_Data['ltl'] = 0.6 #layer to layer spacing
    TPGen_Data['pitch_angle'] = 12.5 #degree
    TPGen_Data['helix_rotations'] = 5
    TPGen_Data['zlayers'] = '' #Number of layer or '' for letting that be determined by geometry
    TPGen_Data['through_rad'] = TPGen_Data['dima']/3
    TPGen_Data['through_layers'] = 3
    
    TPGen_Data['groundplane'] = False
    TPGen_Data['groundindex_X'] = TPGen_Data['helixindex_X'] - 4
    TPGen_Data['groundindex_Y'] = TPGen_Data['helixindex_Y']
    TPGen_Data['ground_rad'] = TPGen_Data['dima']/3
    
    materials = []
    materials.append({'material': TPGen_Data['dielectricname'], 'color': 'b', 'linestyle': '-', 'linewidth': 3, 'alpha': 0.5})
    materials.append({'material': TPGen_Data['dielectricname']+'slide', 'color': 'r', 'linestyle': ':', 'linewidth': 2, 'alpha': 1})
    materials.append({'material': TPGen_Data['conductorname'], 'color': 'k', 'linestyle': '-', 'linewidth': 1, 'alpha': 1})
    materials.append({'material': TPGen_Data['conductorname']+'slide', 'color': 'g', 'linestyle': ':', 'linewidth': 2, 'alpha': 1})
    TPGen_Data['materials'] = materials
    
    return TPGen_Data

def groundplane(hexptarray = 'none', outer_border='none', ground_index = 'none', through_index = 'none', ltl = 'none', dielectric='none', conductor='none', conductorslide='none', zpos='none', through_layers='none', throughrad = 'none', groundrad = 'none', disttol='none', angtol='none'):
    reqdata = [hexptarray, outer_border, ground_index, through_index, ltl, dielectric, conductor, conductorslide, zpos, throughrad, groundrad]
    if 'none' in reqdata:
        raise Exception('exit')
    toolpath3D = []
    throughpoint = {'X':hexptarray[through_index[0]][through_index[1]][0],'Y':hexptarray[through_index[0]][through_index[1]][1]}
    groundpoint = {'X':hexptarray[ground_index[0]][ground_index[1]][0],'Y':hexptarray[ground_index[0]][ground_index[1]][1]}
    
    ground_border = ncircleborder(groundpoint, groundrad, 10)
    through_border = ncircleborder(throughpoint, throughrad, 10)
    #DIELECTRIC SUPPORT LAYER
    #Create triangular decomposition of hexagonal point array 
    ground2Dtoolpath = htt.hexpt2toolpath_ground(hexptarray, dielectric)
    #Remove spaces for through and ground connections
    ground2Dtoolpath = tpt.toolpcut(ground2Dtoolpath, outer_border, False, disttol, angtol)
    #Remove spaces for through and ground connections
    ground2Dtoolpath = tpt.toolpcut(ground2Dtoolpath, ground_border, True, disttol, angtol)
    ground2Dtoolpath = tpt.toolpcut(ground2Dtoolpath, through_border, True, disttol, angtol)
    #Convert to 3D toolpath
    toolpath3D = [*toolpath3D,*tpt.Toolpath2Dto3D(ground2Dtoolpath,zpos)]
    #Add in conduction vias
    toolpath3D = [*toolpath3D, *htt.throughpath(ground_border, through_layers, ltl, zpos, conductor,conductorslide)]
    toolpath3D = [*toolpath3D, *htt.throughpath(through_border, through_layers, ltl, zpos, conductor,conductorslide)]
    #CONDUCTIVE GROUND PLANE
    #Create triangular decomposition of hexagonal point array    
    ground2Dtoolpath = htt.hexpt2toolpath_ground(hexptarray, conductor)
    #Remove spaces for through and ground connections
    ground2Dtoolpath = tpt.toolpcut(ground2Dtoolpath, outer_border, False, disttol, angtol)
    #Remove spaces for through and ground connections
    through_border = ncircleborder(throughpoint, throughrad*2, 10)
    ground2Dtoolpath = tpt.toolpcut(ground2Dtoolpath, through_border, True, disttol, angtol)
    #Convert to 3D toolpath
    toolpath3D = [*toolpath3D,*tpt.Toolpath2Dto3D(ground2Dtoolpath,zpos)]
    return toolpath3D

def nodeborder(mindex, nindex, hexptarray, fraction):
    borderpoints = []
    negmpoint = {'X':(1-fraction)*hexptarray[mindex][nindex][0]+fraction*hexptarray[mindex-1][nindex][0],'Y':(1-fraction)*hexptarray[mindex][nindex][1]+fraction*hexptarray[mindex-1][nindex][1]}
    posmpoint = {'X':(1-fraction)*hexptarray[mindex][nindex][0]+fraction*hexptarray[mindex+1][nindex][0],'Y':(1-fraction)*hexptarray[mindex][nindex][1]+fraction*hexptarray[mindex+1][nindex][1]}
    if mindex%2 == 0:
        npoint = {'X':(1-fraction)*hexptarray[mindex][nindex][0]+fraction*hexptarray[mindex][nindex-1][0],'Y':(1-fraction)*hexptarray[mindex][nindex][1]+fraction*hexptarray[mindex][nindex-1][1]}
    else:
        npoint = {'X':(1-fraction)*hexptarray[mindex][nindex][0]+fraction*hexptarray[mindex][nindex+1][0],'Y':(1-fraction)*hexptarray[mindex][nindex][1]+fraction*hexptarray[mindex][nindex+1][1]}
    borderpoints = [negmpoint,posmpoint,npoint]
    return borderpoints

def ncircleborder(center, radius, lines):
    borderpoints = []
    ZeroCenterPnts = []
    ZeroCenterPnts.append({'X':0, 'Y':radius})
    theta = 2 * math.pi/lines
    for n in range(1, lines):
        newx = ZeroCenterPnts[n-1]['X']*math.cos(theta) - ZeroCenterPnts[n-1]['Y']*math.sin(theta)
        newy = ZeroCenterPnts[n-1]['X']*math.sin(theta) + ZeroCenterPnts[n-1]['Y']*math.cos(theta)
        ZeroCenterPnts.append({'X':newx, 'Y':newy})
    
    for point in ZeroCenterPnts:
        borderpoints.append({'X':point['X']+center['X'], 'Y':point['Y']+center['Y']})

    return borderpoints


def GenerateToolpath(data, target):
    # Unpack data
    # Dimensional tolerances for computational geometry
    disttol = data['disttol']
    angtol = data['angtol']

    # Hexagon dimensions
    dima = data['dima']
    dimb = data['dimb']
    dimc = data['dimc']

    # Number of cells
    cellsX = data['cellsX']
    cellsY = data['cellsY']

    # Print parameters
    tiph = data['tiph']
    ltl = data['ltl']  # layer to layer spacing
    pitch_angle = data['pitch_angle']  # degree
    helix_rotations = data['helix_rotations']

    # Calculations
    effectived = 2 * ((dima + dimc) * dimb / math.pi) ** 0.5
    spacing = math.pi * effectived * math.tan(pitch_angle / 180 * math.pi)
    angleperlayer = 2 * math.pi * ltl / spacing
    if data['zlayers'] == '':
        zlayers = math.floor(spacing * helix_rotations / ltl)
    else:
        zlayers = data['zlayers']

    # Borders
    outer_border = [{'X': 0, 'Y': 0}, {'X': (cellsX + 0.5) * dimb, 'Y': 0}, {'X': (cellsX + 0.5) * dimb, 'Y': cellsY * (dima + dimc)}, {'X': 0, 'Y': cellsY * (dima + dimc)}]

    # CONSTRUCTING 2D GEOMETRY

    # Make a base hexagonal array with target geometry
    # m is the x iterator
    # n is the y iterator
    smallest_m = 2*cellsX
    smallest_n = cellsY

    oversize_factor = 2

    base_array = htt.basearray(dima, dimb, dimc, (oversize_factor * smallest_m), (oversize_factor * smallest_n))

    # shift array to be centered at ~0,0
    shiftx = math.floor((len(base_array) - smallest_m) / 2)
    shifty = math.floor((len(base_array[0]) - smallest_n) / 2)
    shifted_array = htt.shiftarray(base_array, shiftx, shifty)

    # Initialize some lists
    helixhistory = []
    point_array = shifted_array

    # Identify the target cell and collect its geometry
    helix1x = shiftx + data['helixindex_X']
    helix1y = shifty + data['helixindex_Y']
    icellborder1 = htt.hexcellborder(point_array, helix1x, helix1y, 0)
    hstart1 = {'X': icellborder1[0]['X'], 'Y': icellborder1[0]['Y'], 'Z': 0}

    # Through geometry
    through_layers = data['through_layers']

    # square opening around helix start location
    through_border = ncircleborder(hstart1, data['through_rad'], 10)

    toolpath3D = []
    toolpath3D.append({'parse': 'start'})
    zpos = tiph
    # CONSTRUCTING TOOLPATH
    if data['groundplane']:
        groundata = {'hexptarray': point_array, 'outer_border': outer_border, 'ground_index': [helix1x - data['groundindex_X'], helix1y - data['groundindex_Y']], 'through_index': [helix1x, helix1y], 'ltl': ltl, 'dielectric': data['dielectricname'], 'conductor': data['conductorname'], 'conductorslide': data['conductorname'] + 'slide', 'zpos': zpos, 'groundrad': data['ground_rad'], 'throughrad': data['through_rad'], 'disttol': disttol, 'angtol': angtol, 'through_layers': through_layers}
        toolpath3D = [*toolpath3D, *groundplane(**groundata)]
        toolpath2D = [{'startpoint': outer_border[0], 'endpoint': outer_border[1], 'material': data['dielectricname']}, {'startpoint': outer_border[2], 'endpoint': outer_border[3], 'material': data['dielectricname']}]
        toolpath3D = [*toolpath3D, *tpt.Toolpath2Dto3D(toolpath2D, zpos)]
        zpos += ltl
        toolpath3D.append({'parse': 'endoflayer', 'number': 0})
    for k in range(1, zlayers):  # zlayers
        # Handle operations specific to 1st layer
        if k == 1:
            # Build 2D toolpath from hexagonal array
            toolpath2D = htt.hexpt2toolpath(point_array, data['dielectricname'], data['dielectricname'] + 'slide')
            toolpath2D = tpt.toolpcut(toolpath2D, outer_border, False, disttol, angtol)

            # Cut hole for through
            toolpath2D = tpt.toolpcut(toolpath2D, through_border, True, disttol, angtol)

            toolpath2D.append({'startpoint': outer_border[0], 'endpoint': outer_border[1], 'material': data['dielectricname']})
            toolpath2D.append({'startpoint': outer_border[2], 'endpoint': outer_border[3], 'material': data['dielectricname']})

            toolpath3D = [*toolpath3D, *tpt.Toolpath2Dto3D(toolpath2D, zpos)]

            toolpath3D = [*toolpath3D, *htt.throughpath(through_border, through_layers, ltl, zpos, data['conductorname'],data['conductorname']+'slide')]
            cellborder1 = htt.hexcellborder(point_array, helix1x, helix1y, 0)
            helixtoolp1 = htt.helixpath(hstart1, cellborder1, angleperlayer, 0.9*angleperlayer, zpos, ltl, 0, helixhistory, disttol, angtol, data['conductorname'], data['dielectricname'])
            toolpath3D = [*toolpath3D, *helixtoolp1]

        else:
            # Build 2D toolpath from hexagonal array
            toolpath2D = htt.hexpt2toolpath(point_array, data['dielectricname'], data['dielectricname'] + 'slide')
            toolpath2D = tpt.toolpcut(toolpath2D, outer_border, 0, disttol, angtol)

            # Cut out space for embedded helix
            cellborder = htt.hexcellborder(point_array, helix1x, helix1y, 0.1)
            toolpath2D = tpt.toolpcut(toolpath2D, cellborder, 1, disttol, angtol)

            # Add bars at top and bottom
            toolpath2D.append({'startpoint': outer_border[0], 'endpoint': outer_border[1], 'material': data['dielectricname']})
            toolpath2D.append({'startpoint': outer_border[2], 'endpoint': outer_border[3], 'material': data['dielectricname']})

            # Convert to 3D toolpath
            toolpath3D = [*toolpath3D, *tpt.Toolpath2Dto3D(toolpath2D, zpos)]

            # Add in contributions from helix
            cellborder1 = htt.hexcellborder(point_array, helix1x, helix1y, 0)
            helixtoolp1 = htt.helixpath(hstart1, cellborder1, angleperlayer, 0.9 * angleperlayer, zpos, ltl, 0, helixhistory, disttol, angtol, data['conductorname'], data['dielectricname'])
            toolpath3D = [*toolpath3D, *helixtoolp1]

        zpos += ltl
        toolpath3D.append({'parse': 'endoflayer', 'number': k})

    toolpath3D.append({'parse': 'end'})
    # ADDING in Parsing
    # toolpath_parsed = tpt.expandpoints(toolpath3D, ['startpoint','endpoint'], ['X','Y','Z'])
    toolpath_parsed = tpt.parse_endofmotion(toolpath3D, disttol)
    toolpath_parsed = tpt.parse_startofmotion(toolpath_parsed)
    toolpath_parsed = tpt.parse_changemat(toolpath_parsed)
    hierarchylist = ['start', 'changemat', 'endofmotion', 'endoflayer', 'startofmotion', 'end']
    toolpath_parsed = tpt.parse_heirarchy(toolpath_parsed, hierarchylist)

    target[0] = toolpath_parsed
