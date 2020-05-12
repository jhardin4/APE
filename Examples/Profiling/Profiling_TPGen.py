from ToolPathGeneration import ToolPathTools as tpt


def Make_TPGen_Data(material):
    TPGen_Data = {}

    # Material naming
    TPGen_Data['materialname'] = material

    # Structure Geometry
    TPGen_Data['length'] = 5
    TPGen_Data['tiph'] = 0.8  # offset from printing surface

    # Computational Geometry Tolerances
    TPGen_Data['disttol'] = 1e-12  # Distance tolerance
    TPGen_Data['angtol'] = 1e-7  # Angular tolerance

    # Utility parameters
    TPGen_Data['Xoffset'] = 0
    TPGen_Data['Yoffset'] = 0
    TPGen_Data['Zoffset'] = 0

    # Graphing information
    materials = []
    materials.append(
        {
            'material': TPGen_Data['materialname'],
            'color': 'b',
            'linestyle': '-',
            'linewidth': 3,
            'alpha': 0.5,
        }
    )
    materials.append(
        {
            'material': TPGen_Data['materialname'] + 'slide',
            'color': 'r',
            'linestyle': ':',
            'linewidth': 2,
            'alpha': 1,
        }
    )

    TPGen_Data['materials'] = materials

    return TPGen_Data

def GenerateToolpath(data, target):
    # Unpack data

    # Dimensional tolerances for computational geometry
    disttol = data['disttol']

    # line dimensions
    length = data['length']

    # Print parameters
    tiph = data['tiph']
    materialname = data['materialname']

    x_offset = data['Xoffset']
    y_offset = data['Yoffset']
    z_offset = data['Zoffset']
    # -----------------STUFF-----------------------------#

    toolpath3D = []
    toolpath3D.append({'parse': 'start'})
    zpos = tiph
    # CONSTRUCTING TOOLPATH
    # Defining the points
    pointlist= []
    pointlist.append({'X': x_offset, 'Y': y_offset})
    pointlist.append({'X': x_offset + length, 'Y': y_offset})
    
    for n in range(10000):
        pointlist.append({'X': x_offset + length + n, 'Y': y_offset})
    
    toolpath2D = tpt.nPt2ToolPath(pointlist, materialname)
    toolpath3D = [*toolpath3D, *tpt.Toolpath2Dto3D(toolpath2D, zpos+z_offset)]

    toolpath3D.append({'parse': 'end'})
    # ADDING in Parsing

    # toolpath_parsed = tpt.expandpoints(toolpath3D, ['startpoint','endpoint'], ['X','Y','Z'])
    toolpath_parsed = tpt.parse_endofmotion(toolpath3D, disttol)
    toolpath_parsed = tpt.parse_startofmotion(toolpath_parsed)
    toolpath_parsed = tpt.parse_changemat(toolpath_parsed)
    hierarchylist = [
        'start',
        'changemat',
        'endofmotion',
        'endoflayer',
        'startofmotion',
        'end',
    ]
    toolpath_parsed = tpt.parse_heirarchy(toolpath_parsed, hierarchylist)
    target[0] = toolpath_parsed


if __name__ == '__main__':
    data = Make_TPGen_Data('bleh')
    target = [0]
    GenerateToolpath(data, target)

