import bpy
import bmesh
import sys
import os

#bpy.data.objects['Cube'].select = True # Select the default Blender Cube
#bpy.ops.object.mode_set(mode='OBJECT')
#bpy.ops.object.delete() # Delete the selected objects (default blender Cube)

#Define vertices, faces, edges
#verts = [(0,0,0),(0,5,0),(5,5,0),(5,0,0),(0,0,5),(0,5,5),(5,5,5),(5,0,5)]
#faces = [(0,1,2,3), (4,5,6,7), (0,4,5,1), (1,5,6,2), (2,6,7,3), (3,7,4,0)]

#Define mesh and object
#mesh = bpy.data.meshes.new("Cube")
#object = bpy.data.objects.new("Cube", mesh)

#Set location and scene of object
#object.location = bpy.context.scene.cursor.location
#bpy.context.collection.objects.link(object)

#Create mesh
#mesh.from_pydata(verts,[],faces)
#mesh.update(calc_edges=True)

##bpy.ops.object.select_all( action='DESELECT' )
#bpy.data.objects [ 'NurbsPath' ].select_set ( True )
#bpy.context.scene.objects.active = bpy.context.scene.objects['Cube'] # Select the default Blender Cube

#Enter edit mode to extrude
#bpy.ops.object.mode_set(mode='EDIT')
#bpy.ops.mesh.normals_make_consistent(inside=False)

#bm = bmesh.from_edit_mesh(mesh)
#for face in bm.faces:
    #face.select_set ( False )
#bm.faces[1].select_set ( True )

# Show the updates in the viewport
#bmesh.update_edit_mesh(mesh, True)

#bpy.ops.mesh.extrude_faces_move(MESH_OT_extrude_faces_indiv={"mirror":False}, TRANSFORM_OT_shrink_fatten={"value":-5, "use_even_offset":True, "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "release_confirm":False})

#####################################################################################################################################################################################################

bpy.ops.object.mode_set ( mode = 'OBJECT' )
bpy.ops.object.select_all( action='DESELECT' )
bpy.data.objects [ 'Cube' ].select_set ( True )

##################################################################
#export gcode for object_name
##################################################################

bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(-30, -0, -0), "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(True, False, False), "mirror":True, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})

bpy.ops.transform.resize(value=(2, 2, 2), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)

bpy.ops.object.select_all( action='DESELECT' )
bpy.data.objects [ 'Cube.001' ].select_set ( True )

##################################################################
#export gcode for object_name.001
##################################################################

bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(-30, -0, -0), "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(True, False, False), "mirror":True, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})

bpy.ops.transform.resize(value=(2, 2, 2), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)

bpy.ops.object.select_all( action='DESELECT' )
bpy.data.objects [ 'Cube.002' ].select_set ( True )

##################################################################
#export gcode for object_name.002
##################################################################
if os.name == 'posix':
    path = os.path.expanduser('~')+'/Print_With_APE/demo.txt'
elif os.name == 'nt':
    path = os.path.expanduser('~')+'\Print_With_APE\demo.txt'
if os.path.exists(path):
    os.remove(path)
else:
    pass

objid = bpy.context.selected_objects[0].name
obvert = bpy.context.active_object.data.vertices
obedge = bpy.context.active_object.data.edges
obface = bpy.context.active_object.data.polygons
filewrite = open (path, 'a')
filewrite.write('hello \n')
filewrite.write('world \n')
writeobjid = objid+'\n'
filewrite.write(writeobjid)
numv = 0
for v in obvert:
    index = obvert[numv].index
    cox = obvert[numv].co.x
    coy = obvert[numv].co.y
    coz = obvert[numv].co.z
    writedata = 'vindex: '+str(index)+' cox: '+str(cox)+' coy: '+str(coy)+' coz: '+str(coz)+' \n'
    filewrite.write(writedata)
    numv = numv+1
nume = 0
for e in obedge:
    index = obedge[nume].index
    vert0 = obedge[nume].vertices[0]
    vert1 = obedge[nume].vertices[1]
    writedata = 'eindex: '+str(index)+' point-a: '+str(vert0)+' point-b: '+str(vert1)+' \n'
    filewrite.write(writedata)
    nume = nume+1
numf = 0
for f in obface:
    index = obface[numf].index
    writedata = 'findex: '+str(index)
    numv = 0
    for v in f.vertices:
        writedata = writedata+' verticy-'+str(numv)+' '+str(v)
        numv = numv+1
    writedata = writedata+' \n'
    filewrite.write(writedata)
    numf = numf+1
filewrite.close()

fileread = open (path, 'rt')
lstoflsts = []
cmd = ''
val = ''
inum = 0
for i in fileread:
    imod2 = inum%2
    if imod2 == 0:
        cmd = i.split()[0]
    else:
        val = i.split()[0]
        lstoflsts.append([cmd,val])
    inum = inum+1
print(lstoflsts)


print(objid)
print(bpy.context.selected_objects[0].name)

bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)