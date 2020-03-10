from ToolPathGeneration import ToolPathTools as tpt
from mecode.main import G

def Make_TPGen_Data(material):
    TPGen_Data = {}

    # Material naming
    TPGen_Data['materialname'] = material

    # Computational Geometry Tolerances
    TPGen_Data['disttol'] = 1e-12  # Distance tolerance
    TPGen_Data['angtol'] = 1e-7  # Angular tolerance

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
    # Dimensional tolerances for computational geometry
    disttol = data['disttol']
    # Material for geometry
    materialname = data['materialname']

    toolpath3D = []
    toolpath3D.append({'parse': 'start'})

    g = G(print_lines=False)
    g.rename_axis(z='A')
    g.feed(1)
    g.absolute()
    g.move(x=0,y=0,z=1.0)
    g.relative()
    g.toggle_pressure(3)
    g.move(x=25.4*3)
    g.toggle_pressure(3)
    g.feed(2)
    g.move(y=25.4*2)
    g.feed(3)
    g.toggle_pressure(3)
    g.move(x=-25.4*3)
    g.toggle_pressure(3)
    g.feed(4)
    g.move(y=-25.4*2)
    g.move(x=0)
    mecode_toolpath, feeds, extrudings = g.export_APE()

    for path,feed,extruding in zip(mecode_toolpath, feeds,extrudings):
            if extruding:
                toolpath3D += tpt.nPt2ToolPath(path, materialname, feed)

    toolpath3D.append({'parse': 'end'})
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