from ToolPathGeneration import ToolPathTools as tpt
from mecode.main import G
import numpy as np

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

	layer_height = 0.6 #in mm
	print_feed = 1 #in mm/s
	travel_feed = 10 #in mm/s
	com_port = 3
	good_press = 20

	g.rename_axis(z='A')
	g.feed(travel_feed)
	g.absolute()
	
	# Spanning measurement
	g.move(x=28,y=5)
	g.move(z=layer_height)
	g.feed(print_feed)
	g.line_span(padding=15/4.0,dwell=1,distances=[8,16,24,32,40],com_port=com_port,pressure=good_press,travel_feed=travel_feed)

	# Width Measurement
	g.move(x=49,y=5)
	g.move(z=layer_height)
	g.feed(print_feed)
	g.line_meander(width=20,spacings =  np.linspace(3.0,5.0,10),com_port=com_port)

	# Crossing measurement
	g.move(x=4,y=39.4)
	g.move(z=layer_height)
	g.feed(print_feed)
	g.line_crossing(dwell=1,length=30,com_port=com_port,pressure=good_press,travel_feed=travel_feed)

	g.relative()
	g.move(x=0)
	mecode_toolpath, feeds, extrudings = g.export_APE()

	for path,feed,extruding in zip(mecode_toolpath, feeds,extrudings):
			if extruding:
				toolpath3D += tpt.nPt2ToolPath(path, materialname, feed)
	
	# Set up different pressures in modified meander
	pressures = np.linspace(1.05,1.5,10)
	for ind,pressure in enumerate(pressures):
		for path in toolpath3D[6+ind*3:6+ind*3+3]:
			path['mpo'] = pressure

	# Slightly over extrude during line crossing
	toolpath3D[-1]['mpo'] = 1.2

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