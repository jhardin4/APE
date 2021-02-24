import bpy
import time

activeobject = bpy.context.active_object
bpy.ops.transform.resize ( value = ( 0.5, 0.5, 0.5 ) )
time.sleep ( 1 )
bpy.ops.transform.resize ( value = ( 2, 2, 2 ) )
