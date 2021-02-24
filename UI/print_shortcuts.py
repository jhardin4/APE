#!/usr/bin/env python


#  Exports selected objects from Blender to various 3D slicing or printing applications or servers
#  Copyright (C) 2017 S0AndS0
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 2
#  of the License.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


# Tip to future self; use 'Ctrl F' then 'Esc` to bring up find menu & exit from search
#  then under 'Properties' select 'Show Margin' & set 'Margin Column' to '120' to
#  ensure line lengths do not exced limits defined by https://wiki.blender.org/index.php/Dev:Doc/Code_Style
# Furthermore, prior to public pushes to any Git server check that code formatting is
#  compliant with PEP 8 https://www.python.org/dev/peps/pep-0008/
# How to access values within bl_info latter within this script
#   print(bl_info.get('name'))

#1856 is the beginning of button UI elements
bl_info = {
    "name": "3DPrint Short Cuts",
    "author": "S0AndS0",
    "version": (1, 6),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > 3D-Printing",
    "description": "Enables translation to GCode without leaving Blender & uploading to OctoPrint or Repetier server(s)",
    "warning": "Untested on Mac & Win. Uses Curl for server interactions, and Slic3r or CuraEngine for GCode translations.",
    "wiki_url": "https://s0ands0.github.io/3D_Printing/blender/addons/3dprint-short-cuts/readme.html",
    "category": "Import-Export",
}


import bpy
import os
import platform
import subprocess
import json

from bpy.types import (
    Operator,
    Panel,
    PropertyGroup)
from bpy.props import (
    BoolProperty,
    EnumProperty,
    StringProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty)


this_addons_name = bpy.path.display_name_from_filepath(__file__)
this_addons_category = bl_info.get('name')

Target_render_engine = 'BLENDER_GAME'
Target_material_mode = 'GLSL'
Target_viewport_shade = 'TEXTURED'

if 'Linux' in platform.system():
    slic3r_exec_name = 'slic3r'
    slic3r_exec_dir = ''
    curaengine_exec_dir = ''
    curaengine_exec_name = 'CuraEngine'
    curl_exec_dir = ''
    curl_exec_name = 'curl'
elif 'Windows' in platform.system():
    slic3r_exec_name = 'slic3r-console.exe'
    slic3r_exec_dir = ''
    curaengine_exec_dir = ''
    curaengine_exec_name = 'CuraEngine'
    curl_exec_dir = ''
    curl_exec_name = 'curl'
elif 'Darwin' in platform.system():
    slic3r_exec_name = 'slic3r'
    slic3r_exec_dir = 'Slic3r.app/Contents/MacOS'
    curaengine_exec_dir = ''
    curaengine_exec_name = 'CuraEngine'
    curl_exec_dir = ''
    curl_exec_name = 'curl'
else:
    raise Exception('## Did not understand platform.system(): {0}'.format(platform.system()))


#-------------------------------------------------------------------------
#   Global variables & imports above, bellow custom classes alphabeticly organized
#-------------------------------------------------------------------------


class Blender(object):
    """
    # This class contains short-cuts to various Blender operations such as getting an object by name,
    #  renaming an object, parenting two object, adding empty & plane objects, and importing & exporting
    #  of various file types.
    """
    def __init__(self, context = bpy.context):
        self.blender_version_main = bpy.app.version[0]
        self.blender_version_sub = bpy.app.version[1]
        self.selected_objects = context.selected_objects
        # Slic3r panel settings for this instance
        self.slic3r_exec_dir = context.scene.slic3r_exec_dir
        self.slic3r_exec_name = context.scene.slic3r_exec_name
        self.slic3r_conf_path = context.scene.slic3r_conf_path
        self.slic3r_post_script = context.scene.slic3r_post_script
        self.slic3r_extra_args = context.scene.slic3r_extra_args
        self.slic3r_repaired_parent_name = context.scene.slic3r_repaired_parent_name
        self.slic3r_gcode_directory = context.scene.slic3r_gcode_directory
        # Export STL settings
        self.export_stl_directory = context.scene.export_stl_directory
        self.export_stl_axis_forward = context.scene.export_stl_axis_forward
        self.export_stl_axis_up = context.scene.export_stl_axis_up
        self.export_stl_ascii = context.scene.export_stl_ascii
        self.export_stl_check_existing = context.scene.export_stl_check_existing
        self.export_stl_global_scale = context.scene.export_stl_global_scale
        self.export_stl_use_scene_unit = context.scene.export_stl_use_scene_unit
        # Import OBJ settings
        self.import_obj_directory = context.scene.import_obj_directory
        self.import_obj_axis_forward = context.scene.import_obj_axis_forward
        self.import_obj_axis_up = context.scene.import_obj_axis_up
        self.import_obj_use_edges = context.scene.import_obj_use_edges
        self.import_obj_use_smooth_groups = context.scene.import_obj_use_smooth_groups
        self.import_obj_use_split_objects = context.scene.import_obj_use_split_objects
        self.import_obj_use_split_groups = context.scene.import_obj_use_split_groups
        self.import_obj_use_groups_as_vgroups = context.scene.import_obj_use_groups_as_vgroups
        self.import_obj_use_image_search = context.scene.import_obj_use_image_search
        self.import_obj_split_mode = context.scene.import_obj_split_mode
        self.import_obj_global_clamp_size = context.scene.import_obj_global_clamp_size
        #
        self.export_stl_treat_selected_as = context.scene.export_stl_treat_selected_as

    # Returns 'stl_path' after running bpy.ops.export_mesh.stl
    def export_stl(self, stl_path = None, objects = None):
        """
        # Copy/paste-able block
        BLDR = Blender(context)
        export_stl_output = BLDR.export_stl(stl_path= None, objects = None)
        # stl_path should be a file path to save object(s) to in STL format
        # object should be either an object or list of objects to export to
        #  file path defined by stl_path
        # Note this method will not export objects that have the type 'EMPTY'
        #  to avoid causing errors with slicers & repair operations on such objects
        """
        if stl_path is None:
            raise Exception('No "stl_path" defined for Blender.export_stl(stl_path="?", objects="?")')
        if objects is None:
            raise Exception('No "object" defined for Blender.export_stl(stl_path="?", objects="?")')
        # De-select all objects then select target objects
        bpy.ops.object.select_all(action='DESELECT')
        objs = []
        if isinstance(objects, list):
            for obj in objects:
                if obj.type != 'EMPTY':
                    print('## Object name being exported:', obj.name)
                    obj.select_set ( True )
                    objs += [obj]
                else:
                    print('## Skipping selection of object', obj.name, ":", obj.type)
        elif objects:
            if objects.type != 'EMPTY':
                print('## Object name being exported:', objects.name)
                objects.select_set ( True )
                objs += [objects]
            else:
                print('## Scipping selection of object', objects.name, ":", objects.type)
        if len(objs) >= 1:
            print('## Exporting',objs[0].name)
            if self.blender_version_main is 2 and self.blender_version_sub >= 77:
                export_mesh_stl_output = bpy.ops.export_mesh.stl(
                    filepath = stl_path,
                    check_existing = self.export_stl_check_existing,
                    axis_forward = self.export_stl_axis_forward,
                    axis_up = self.export_stl_axis_up,
                    filter_glob = '*.stl', use_selection = True,
                    global_scale = self.export_stl_global_scale,
                    use_scene_unit = self.export_stl_use_scene_unit,
                    ascii = self.export_stl_ascii,
                    use_mesh_modifiers = True, batch_mode = 'OFF')
                print('###', 'bpy.ops.export_mesh.stl(filepath =', stl_path,
                    ', check_existing =', self.export_stl_check_existing,
                    ', axis_forward =', self.export_stl_axis_forward,
                    ', axis_up =', self.export_stl_axis_up,
                    ", filter_glob = '*.stl', use_selection = True,",
                    'global_scale =', self.export_stl_global_scale,
                    ', use_scene_unit =', self.export_stl_use_scene_unit,
                    ', ascii =', self.export_stl_ascii,
                    ", use_mesh_modifiers = True, batch_mode = 'OFF')")
                #return stl_path
            elif self.blender_version_main is 2 and self.blender_version_sub <= 76:
                export_mesh_stl_output = bpy.ops.export_mesh.stl(
                    filepath = stl_path,
                    check_existing = self.export_stl_check_existing,
                    axis_forward = self.export_stl_axis_forward,
                    axis_up = self.export_stl_axis_forward,
                    filter_glob = '*.stl',
                    global_scale = self.export_stl_global_scale,
                    use_scene_unit = self.export_stl_use_scene_unit,
                    ascii = self.export_stl_ascii,
                    use_mesh_modifiers=True)
                print('###', 'bpy.ops.export_mesh.stl(filepath =', stl_path,
                    ', check_existing =', self.export_stl_check_existing,
                    ', axis_forward =', self.export_stl_axis_forward,
                    ', axis_up =', self.export_stl_axis_forward,
                    ", filter_glob = '*.stl',",
                    'global_scale =', self.export_stl_global_scale,
                    ', use_scene_unit =', self.export_stl_use_scene_unit,
                    ', ascii =', self.export_stl_ascii,
                    ', use_mesh_modifiers=True)')
        # Hide exported object(s) & return stl_path
        if isinstance(objs, list):
            for obj in objs:
                obj.hide_set ( True )
        path_exists = Os.path_exists(path = stl_path)
        return path_exists

    # Returns imported object if file path exists else raises an exception
    def import_obj(self, path = None):
        """
        # Copy/paste-able block

        """
        path_exists = Os.path_exists(path = path)
        if path_exists is False:
            raise Exception('Could not find OBJ file at: {0}'.format(path))
        else:
            import_scene_obj_output = bpy.ops.import_scene.obj(
                filepath = path_exists,
                axis_forward = self.import_obj_axis_forward,
                axis_up = self.import_obj_axis_up,
                filter_glob = "*.obj;*.mtl",
                use_edges = self.import_obj_use_edges,
                use_smooth_groups = self.import_obj_use_smooth_groups,
                use_split_objects = self.import_obj_use_split_objects,
                use_split_groups = self.import_obj_use_split_groups,
                use_groups_as_vgroups = self.import_obj_use_groups_as_vgroups,
                use_image_search = self.import_obj_use_image_search,
                split_mode = self.import_obj_split_mode,
                global_clamp_size = self.import_obj_global_clamp_size)
            latest_selected_obj = bpy.context.selected_objects[0]
            return latest_selected_obj

    # Returns object after setting 'show_name' & 'show_x_ray' to 'True'
    @staticmethod
    def expose_object_name(object_to_expose = None):
        """
        # Copy/paste-able block
        obj = Blender.expose_object_name(object_to_expose = Blender.get_object_by_name(object_name = 'Slic3r_Repaired')
        # Returns object after setting 'show_name' & 'show_x_ray' to 'True'
        """
        if object_to_expose is None:
            raise Exception('Could not find object to expose the name of')
        obj = object_to_expose
        print('# Blender.expose_object_name setting "show_name" & "show_x_ray" to "True" on Object:', obj.name)
        obj.show_name = True
        obj.show_x_ray = True
        return obj

    # Returns 'None' if no object exsists for given name or returns the Object
    @staticmethod
    def get_object_by_name(object_name = None):
        """
        # Copy/paste-able block
        obj = Blender.get_object_by_name(object_name = 'Cube')
        # Returns 'None' if no object exsists for given name or returns the Object
        """
        if object_name is None:
            raise Exception('No object_name defined to searh for')
        obj = bpy.data.objects.get(object_name)
        if obj:
            print('# Blender.get_object_by_name returning object named:', obj.name)
        else:
            print('# Blender.get_object_by_name returning:', obj)
        return obj

    # Returns imported text object, reloads text contence if object alredy exsists
    @staticmethod
    def import_text(path = None):
        """
        # Copy/paste-able block
        obj = Blender.import_text(path = /tmp/Cube.gcode)
        # Returns imported text object, reloads text contence if object alredy exsists
        # This is a short cut to bpy.data.texts and bpy.ops.text.open with checks for
        #  preexisting files already loaded into current Blender session.
        """
        if path is None:
            raise Exception('Blender.import_text needs a file path to import text from.')
        if os.path.exists(path):
            filename = bpy.path.basename(path)
        else:
            raise Exception('Blender.import_text needs a file path to import text from.')
        text_obj = bpy.data.texts.get(filename)
        if text_obj is None:
            bpy.ops.text.open(filepath = path)
        else:
            text_obj.clear()
            bpy.data.texts.remove(text_obj)
            bpy.ops.text.open(filepath = path)
        text_obj = bpy.data.texts.get(filename)
        return text_obj

    # Returns object after making a new empty at specified 'location'
    @staticmethod
    def new_empty(location = (0, 0, 0)):
        """
        # Copy/paste-able block
        obj = Blender.new_empty(location=(0, 0, 0))
        # Returns object after making a new empty at specified 'location'
        """
        bpy.ops.object.add(type='EMPTY', location = location)
        new_empty_output = bpy.context.active_object
        print('# Blender.new_empty returning new empty object named:', new_empty_output.name)
        return new_empty_output

    # Returns object after placing on self.preview_layer
    @staticmethod
    def new_plane(name = None, layers = 1):
        """
        # Copy/paste-able block
        new_plane_obj = Blender.new_plane(name = None, layers = 1)
        # Returns object after placing on self.preview_layer
        """
        obj = Blender.get_object_by_name(object_name = name)
        if obj is None:
            layers = Blender.return_layer_list(layer = layers)
            bpy.ops.mesh.primitive_plane_add(layers = layers)
            bpy.context.object.name = name
            # The above seems to work but will fail if this addon is called from the command line instead of UI
            # The following would fail to target at all
            # bpy.data.meshes[-1].name = object_name
            # The following would target Suzanne & other objects
            # bpy.data.objects[-1].name = object_name
            obj = Blender.get_object_by_name(object_name = name)
        return obj

    # Opens a web-browser or tab pointed at 'url'
    @staticmethod
    def open_browser(url = None):
        """
        # Copy/paste-able block
        Blender.open_browser(url = localhost:8080)
        """
        if url is None:
            raise Exception('No URL provided to Blender.open_browser(url="?")')
        bpy.ops.wm.url_open(url=url)

    # Returns parent_object after parenting to child_object
    @staticmethod
    def parent_object_a_to_b(parent_object = None, child_object = None):
        """
        # Copy/paste-able block
        obj = Blender.parent_object_a_to_b(parent_object = empty_obj, child_object = child_object)
        # Returns parent_object after parenting to child_object
        """
        if child_object is None or parent_object is None:
            raise Exception('Parent object or child object is missing')
        print('# Blender.parent_object_a_to_b is parenting', child_object.name, 'to:', parent_object.name)
        child_object.parent = parent_object
        return parent_object

    # Makes a named empty if needed then returns output of parent_object_a_to_b which should be the named empty Object
    @staticmethod
    def parent_object_to_named_empty(empty_name = 'Slic3r_Repaired', empty_location = (0, 0, 0), child_object = None):
        """
        # Copy/paste-able block
        obj = Blender.parent_object_to_named_empty(empty_name = 'Slic3r_Repaired', empty_location = (0, 0, 0), child_object = None)
        # Makes a named empty if needed then returns output of parent_object_a_to_b which should be the named empty Object
        """
        if child_object is None:
            raise Exception('Could not find child object to parent to named empty')
        empty_obj = Blender.get_object_by_name(object_name = empty_name)
        if empty_obj is None:
            empty_obj = Blender.new_empty(location = empty_location)
            rename_object_output = Blender.rename_object(object_to_name = empty_obj, new_object_name = empty_name)
            expose_object_name_output = Blender.expose_object_name(object_to_expose = empty_obj)
        # Parent object to empty & return the results
        parent_object_a_to_b_output = Blender.parent_object_a_to_b(parent_object = empty_obj, child_object = child_object)
        return parent_object_a_to_b_output

    # Returns renamed object
    @staticmethod
    def rename_object(object_to_name = None, new_object_name = 'Slic3r_Repaired'):
        """
        # Copy/paste-able block
        obj = Blender.rename_object(object_to_name = 'Empty', new_object_name = 'Slic3r_Repaired')
        # Returns renamed object
        """
        if object_to_name is None:
            raise Exception('Could not find object to name')
        old_name = object_to_name.name
        object_to_name.name = new_object_name
        print('# Blender.rename_object returning object renamed from "{0}" to "{1}"'.format(old_name, new_object_name))
        return object_to_name

    # Returns a list of 19 Falses & 1 True
    @staticmethod
    def return_layer_list(layer = 1):
        """
        # Copy/paste-able block
        layers = Blender.return_layer_list(layer = 1)
        # Returns a list of 19 Falses & 1 True
        """
        layers = []
        for count in range(0, 20):
            if count != layer:
                layers += [False]
            else:
                layers += [True]
        return layers


class CuraEngine(object):
    """
    # Short-cuts to CuraEngine slice operations
    """
    def __init__(self, context = bpy.context):
        self.selected_objects = context.selected_objects
        self.curaengine_exec_dir = context.scene.curaengine_exec_dir
        self.curaengine_exec_name = context.scene.curaengine_exec_name
        self.curaengine_conf_path = context.scene.curaengine_conf_path
        self.curaengine_extra_args = context.scene.curaengine_extra_args
        self.curaengine_gcode_directory = context.scene.curaengine_gcode_directory
        self.curaengine_preview_gcode = context.scene.curaengine_preview_gcode
        #
        self.export_stl_treat_selected_as = context.scene.export_stl_treat_selected_as

    def slice_stl(self, stl_path=None, gcode_path=None):
        """
        # Copy/paste-able block
        CE = CuraEngine
        slice_output = slice_stl(stl_path=None, gcode_path=None)
        """
        SP = SubProcess()
        args = []
        if os.path.exists(self.curaengine_conf_path):
            args += ['-j', self.curaengine_conf_path]
        if self.curaengine_extra_args:
            extra_args = []
            for arg in enumerate(self.curaengine_extra_args.split(' ')):
                extra_args += [arg[1]]
            args.extend(extra_args)
        if 'Merge' in self.export_stl_treat_selected_as:
            for stl in stl_path:
                args += ['-l']
                args += [stl]
        else:
            args += [stl_path]
        args += ['-o', gcode_path]
        curaengine_slice_stl_output = SP.curaengine_check_call(ops = args)
        # curaengine_slice_stl_output = self.curaengine_exec(ops = args)
        return curaengine_slice_stl_output


class Formatted_output(object):
    """
    # This is a container for holding output of various operations within an object returned
    #  to calling bpy.types.Operator classes.
    # Example of how repair_through_slic3r(context) loaded the 'blender_export_stl_output' value
    #  when 'Individual' or 'Merge' is detected within bpy.context.scene.export_stl_treat_selected_as
    operation_output.blender_export_stl_output += [BLDR.export_stl(stl_path = stl_path, objects = object)]
    # Example of reporting within: slic3r_repair_button(Operator)
    def execute(self, context):
        if not context.selected_objects:
            raise Exception('Please select some objects first.')
        op = Selected_objects(context)
        op_output = op.repair_through_slic3r(context)
        op_output.calling_operator = 'slic3r_repair_button(Operator)'
        formated_output = Formatted_output.return_output(op_output)
        for info in formated_output:
            self.report({'INFO'}, info)
        info = ('# ' + op_output.calling_operator + 'finished')
        self.report({'INFO'}, info)
        return {'FINISHED'}
    # Example output of 'operation_output.blender_export_stl_output' value
    Info: # Exported: /tmp/blender_VZ4s7a/Cube.stl
    """
    calling_operator = None
    blender_export_stl_output = []
    blender_import_obj_output = []
    blender_imported_objects = []
    blender_imported_texts = []
    slic3r_repair_stl_output = []
    slice_stl_output = []
    curaengine_slice_stl_output = []
    mkdir_output = []
    rm_file_output = []
    curl_ops = []
    curl_log = []
    octoprint_folders = []
    octoprint_machinecode_files = []
    octoprint_model_files = []

    # Returns a list of formated output for calling operations to loop over for printing info to user interface
    def return_output(self):
        """
        # This returns a list of formated output from values set by calling operations
        """
        if self.calling_operator:
            output_list = ['# Formatted Output {0} #'.format(self.calling_operator)]
        else:
            output_list = ['# Formatted Output #']
        mkdir_output = self.return_formated_list(output_header = 'Made directory', parsabel_output = self.mkdir_output)
        if mkdir_output:
            output_list.extend(mkdir_output)
        blender_export_stl_output = self.return_formated_list(output_header = 'Exported', parsabel_output = self.blender_export_stl_output)
        if blender_export_stl_output:
            output_list.extend(blender_export_stl_output)
        blender_import_obj_output = self.return_formated_list(output_header = 'Imported OBJ file', parsabel_output = self.blender_import_obj_output)
        if blender_import_obj_output:
            output_list.extend(blender_import_obj_output)
        if isinstance(self.blender_imported_objects, list):
            for o in self.blender_imported_objects:
                if o:
                    output_list += ['# Imported object name: {0}'.format(o.name)]
        elif self.blender_imported_objects:
            output_list += ['# Imported object name: {0}'.format(self.blender_imported_objects.name)]
        if isinstance(self.blender_imported_texts, list):
            for i in self.blender_imported_texts:
                if i:
                    output_list += ['# Imported text file: {0}'.format(i.name)]
        elif self.blender_imported_texts:
            output_list += ['# Imported text file: {0}'.format(self.blender_imported_texts.name)]
        rm_file_output = self.return_formated_list(output_header = 'Removed temporary file', parsabel_output = self.rm_file_output)
        if rm_file_output:
            output_list.extend(rm_file_output)
        return output_list

    # Returns a list or None
    @staticmethod
    def return_formated_list(parsabel_output=None, output_header=None):
        """
        # Copy / paste block
        output_list = Formatted_output.return_formated_list(parsabel_output = None, output_header = None)
        # This is to cut-down on redundent repitition in return_output method
        """
        if parsabel_output != None and output_header != None:
            output_list = []
            if isinstance(parsabel_output, list):
                for o in parsabel_output:
                    if o:
                        output_list += ['# {0}: {1}'.format(output_header, o)]
            elif parsabel_output:
                output_list += ['# {0}: {1}'.format(output_header, parsabel_output)]
        else:
            output_list = None
        # print('# Formatted_output.return_formated_list returning: {0}'.format(output_list))
        return output_list


class OctoPrint(object):
    """
    Short cuts to OctoPrint methods
    """
    def __init__(self, context = bpy.context):
        # Example of inheriting this class's values
        # super(OctoPrint, self).__init__()
        # self.arg = arg
        self.selected_objects = context.selected_objects
        self.log_level = context.scene.log_level
        # Connection settings
        self.octoprint_host = context.scene.octoprint_host
        self.octoprint_port = context.scene.octoprint_port
        self.octoprint_user = context.scene.octoprint_user
        self.octoprint_pass = context.scene.octoprint_pass
        self.octoprint_x_api_key = context.scene.octoprint_x_api_key
        self.octoprint_api_path = context.scene.octoprint_api_path
        self.octoprint_new_dir = context.scene.octoprint_new_dir
        # Where to save uploaded files to
        self.octoprint_save_stl_dir = context.scene.octoprint_save_stl_dir
        self.octoprint_save_gcode_dir = context.scene.octoprint_save_gcode_dir
        # Server file & directory listing settings
        self.octoprint_target_search_dir = context.scene.octoprint_target_search_dir
        self.octoprint_temp_dir = context.scene.octoprint_temp_dir
        # Server slicer settings
        if context.scene.octoprint_slice_uploaded_stl:
            self.octoprint_slice_uploaded_stl = context.scene.octoprint_slice_uploaded_stl
            self.octoprint_slice_printerProfile = context.scene.octoprint_slice_printerProfile
            self.octoprint_slice_slicer = context.scene.octoprint_slice_slicer
            self.octoprint_slice_Profile = context.scene.octoprint_slice_Profile
            self.octoprint_slice_Profile_ops = context.scene.octoprint_slice_Profile_ops
            self.octoprint_slice_position_x = context.scene.octoprint_slice_position_x
            self.octoprint_slice_position_y = context.scene.octoprint_slice_position_y
            # self.octoprint_target_screen = context.scene.octoprint_target_screen
            # self.octoprint_target_3dview = context.scene.octoprint_target_3dview
        #
        if context.scene.octoprint_port:
            self.host_url = context.scene.octoprint_host + ':' + context.scene.octoprint_port
        else:
            self.host_url = context.scene.octoprint_host

    def download_json_file_listing(self, target_search_dir = None):
        """
        # Copy/paste-able block
        OP = OctoPrint(context)
        OP.download_json_file_listing(target_search_dir = None)
        """
        SP = SubProcess()
        download_file_path = os.path.join(self.octoprint_temp_dir, 'file_list.json')
        curl_header = self.return_curl_header_lists()
        curl_ops = curl_header.curl_ops
        curl_log = curl_header.curl_log
        if self.octoprint_target_search_dir and self.octoprint_target_search_dir != 'RECURSIVE':
            curl_ops += ['{0}{1}/{2}?recursive=true'.format(self.host_url, self.octoprint_api_path, self.octoprint_target_search_dir), '-o', download_file_path]
            if self.log_level != 'QUITE':
                curl_log += ['{0}{1}/{2}?recursive=true'.format(self.host_url, self.octoprint_api_path, target_search_dir), '-o', download_file_path]
        else:
            curl_ops += ['{0}{1}?recursive=true'.format(self.host_url, self.octoprint_api_path), '-o', download_file_path]
            if self.log_level != 'QUITE':
                curl_log += ['{0}{1}?recursive=true'.format(self.host_url, self.octoprint_api_path), '-o', download_file_path]
        octoprint_download_json_file_listing_output = SP.curl_check_call(ops = curl_ops, log_ops = curl_log)
        # return octoprint_download_json_file_listing_output
        return download_file_path

    def return_file_list_as_object(self, dict_obj = None, root_dir = True):
        output = Formatted_output()
        if root_dir:
            if self.octoprint_target_search_dir:
                dictionary = dict_obj['children']
            else:
                dictionary = dict_obj['files']
        else:
            dictionary = dict_obj['children']
        output.octoprint_folders = []
        output.octoprint_machinecode_files = []
        output.octoprint_model_files = []
        for item in dictionary:
            if item['type'] == 'folder':
                output.octoprint_folders += [item]
            elif item['type'] == 'machinecode':
                output.octoprint_machinecode_files += [item]
            elif item['type'] == 'model':
                output.octoprint_model_files += [item]
        return output

    def return_curl_header_lists(self):
        """
        # Copy/paste-able block
        curl_header = self.return_curl_header_lists()
        curl_ops = curl_header.curl_ops
        curl_log = curl_header.curl_log
        """
        output = Formatted_output()
        curl_ops = ['-f', '-k', '--connect-timeout', '15']
        curl_log = []
        if self.log_level != 'QUITE':
            curl_log.extend(curl_ops)
        if self.octoprint_x_api_key:
            curl_ops += ['-H', 'X-Api-Key: {0}'.format(self.octoprint_x_api_key)]
            if self.log_level == 'VERBOSE':
                curl_log += ['-H', 'X-Api-Key: {0}'.format(self.octoprint_x_api_key)]
            elif self.log_level == 'SCRUBBED':
                curl_log += ['-H', 'X-Api-Key: X-API-KEY']
        if self.octoprint_user and self.octoprint_pass:
            curl_ops += ['-u', '{0}:{1}'.format(self.octoprint_user, self.octoprint_pass)]
            if self.log_level == 'VERBOSE':
                curl_log += ['-u', '{0}:{1}'.format(self.octoprint_user, self.octoprint_pass)]
            elif self.log_level == 'SCRUBBED':
                curl_log += ['-u', 'USER:PASS']
        output.curl_ops = curl_ops
        output.curl_log = curl_log
        return output

    def upload_file(self, gcode_path = None, stl_path = None):
        """
        # Copy/paste-able block
        OP = OctoPrint(context)
        OP.upload_file(gcode_path = None, stl_path = None)
        """
        SP = SubProcess()
        if gcode_path:
            file_name = bpy.path.basename(gcode_path)
        elif stl_path:
            file_name = bpy.path.basename(stl_path)
        # Build an array of options to send to curl command
        curl_header = self.return_curl_header_lists()
        # print('## curl_header:', curl_header)
        # print('## self.return_curl_header_lists()', self.return_curl_header_lists())
        curl_ops = curl_header.curl_ops
        curl_log = curl_header.curl_log
        curl_ops += ['-H', 'Content-Type: multipart/form-data']
        if self.log_level != 'QUITE':
            curl_log += ['-H', 'Content-Type: multipart/form-data']
        if gcode_path:
            if gcode_dir:
                curl_ops += ['-F', 'path={0}/{1}'.format(self.octoprint_save_gcode_dir, file_name)]
                if self.log_level != 'QUITE':
                    curl_log += ['-F', 'path={0}/{1}'.format(self.octoprint_save_gcode_dir, file_name)]
        elif stl_path:
            if self.octoprint_save_stl_dir:
                curl_ops += ['-F', 'path={0}/'.format(self.octoprint_save_stl_dir)]
                if self.log_level != 'QUITE':
                    curl_log += ['-F', 'path={0}/'.format(self.octoprint_save_stl_dir)]
        if gcode_path:
            curl_ops += ['-F', 'file=@{0}'.format(gcode_path), '{0}{1}'.format(self.host_url, self.octoprint_api_path),]
            if self.log_level == 'VERBOSE':
                curl_log += ['-F', 'file=@{0}'.format(gcode_path), '{0}{1}'.format(self.host_url, self.octoprint_api_path),]
            elif self.log_level == 'SCRUBBED':
                curl_log += ['-F', 'file=@{0}'.format(gcode_path), 'HOST{0}'.format(api_path),]
        elif stl_path:
            curl_ops += ['-F', 'file=@{0}'.format(stl_path), '{0}{1}'.format(self.host_url, self.octoprint_api_path),]
            if self.log_level == 'VERBOSE':
                curl_log += ['-F', 'file=@{0}'.format(stl_path), '{0}{1}'.format(self.host_url, self.octoprint_api_path),]
            elif self.log_level == 'SCRUBBED':
                curl_log += ['-F', 'file=@{0}'.format(stl_path), 'HOST{0}'.format(self.octoprint_api_path),]
        upload_file_output = SP.curl_check_call(ops = curl_ops, log_ops = curl_log)
        return upload_file_output

    def slice_stl(self, stl_path=''):
        """
        # Copy/paste-able block
        OP = OctoPrint(context)
        OP.slice_stl(stl_path = None)
        """
        SP = SubProcess()
        stl_name = bpy.path.basename(stl_path)
        stl_file_name = stl_name.split('.')
        sliced_gcode_name = '{0}.gcode'.format(stl_file_name[0])
        curl_header = self.return_curl_header_lists()
        curl_ops = curl_header.curl_ops
        curl_log = curl_header.curl_log
        curl_ops += ['-X', 'POST', '-H', 'Content-Type: application/json']
        if self.log_level != 'QUITE':
            curl_log += ['-X', 'POST', '-H', 'Content-Type: application/json']
        slicer_ops = ['"command": "{0}", '.format('slice')]
        slicer_ops += ['"slicer": "{0}", '.format(self.octoprint_slice_slicer)]
        slicer_ops += ['"gcode": "{0}", '.format(sliced_gcode_name)]
        if self.octoprint_slice_printerProfile:
            slicer_ops += ['"printerProfile": "{0}", '.format(self.octoprint_slice_printerProfile)]
        if self.octoprint_slice_Profile:
            slicer_ops += ['"profile": "{0}", '.format(self.octoprint_slice_Profile)]
        if self.octoprint_slice_Profile_ops:
            profile_ops = []
            for profile_op in enumerate(self.octoprint_slice_Profile_ops.split(', ')):
                split_profile_op = profile_op[1].split(':')
                if split_profile_op[0] and split_profile_op[1]:
                    # Format and add to main slicer_ops list
                    slicer_ops += ['"profile.{0}": {1}, '.format(split_profile_op[0], split_profile_op[1])]
        if self.octoprint_slice_position_x and self.octoprint_slice_position_y:
            slicer_ops += ['"position": {"x": {0}, "y": {1}}, '.format(self.octoprint_slice_position_x, self.octoprint_slice_position_y)]
        else:
            slicer_ops += ['"position": {"x": 0, "y": 0}, ']
        slicer_ops += ['"print": false']
        # Convert slicer_ops list to string before adding to curl_ops list
        slicer_string = ''.join(slicer_ops)
        curl_ops += ['-d', '{'+slicer_string+'}']
        if self.log_level != 'QUITE':
            curl_log += ['-d', '{'+slicer_string+'}']

        # Finalize curl options with the URL to the uploaded STL file
        if self.octoprint_save_stl_dir:
            curl_ops += ['{0}{1}/{2}/{3}'.format(self.host_url, self.octoprint_api_path, self.octoprint_save_stl_dir, stl_name)]
            if self.log_level == 'VERBOSE':
                curl_log += ['{0}{1}/{2}/{3}'.format(self.host_url, self.octoprint_api_path, self.octoprint_save_stl_dir, stl_name)]
            elif self.log_level == 'SCRUBBED':
                curl_log += ['HOST/{0}/{1}/{2}'.format(self.octoprint_api_path, self.octoprint_save_stl_dir, stl_name)]
        else:
            curl_ops += ['{0}{1}/{2}'.format(self.host_url, self.octoprint_api_path, stl_name)]
            if self.log_level == 'VERBOSE':
                curl_log += ['{0}{1}/{2}'.format(self.host_url, self.octoprint_api_path, stl_name)]
            elif self.log_level == 'SCRUBBED':
                curl_log += ['HOST/{0}/{1}'.format(self.octoprint_api_path, stl_name)]
        slice_stl_output = SP.curl_check_call(ops = curl_ops, log_ops = curl_log)
        return slice_stl_output

    def mkdir(self, path=''):
        """
        # Copy/paste-able block
        OP = OctoPrint(context)
        OP.mkdir(path = None)
        """
        SP = SubProcess()
        exsistent_dirs = ''
        for dir in enumerate(path.split('/')):
            if exsistent_dirs:
                print('# Existent dirs #', exsistent_dirs)
                check_dir = exsistent_dirs + '/' + dir[1]
            else:
                check_dir = dir[1]
            try:
                curl_header = self.return_curl_header_lists()
                curl_ops = curl_header.curl_ops
                curl_log = curl_header.curl_log
                curl_ops += ['-G']
                if self.log_level != 'QUITE':
                    curl_log += ['-G']
                curl_ops += ['-H', 'recursive=true', '{0}{1}/{2}'.format(self.host_url, self.octoprint_api_path, check_dir)]
                if self.log_level != 'QUITE':
                    curl_log += ['-H', 'recursive=true', '{0}{1}/{2}'.format(self.host_url, self.octoprint_api_path, check_dir)]
                check_dir_output = SP.curl_check_call(ops = curl_ops, log_ops = curl_log)
                return check_dir_output
            except subprocess.CalledProcessError as process_error:
                print('# Directory does NOT exist #', dir[1])
                if exsistent_dirs:
                    dir_path = exsistent_dirs
                    new_dir = dir[1]
                    curl_header = self.return_curl_header_lists()
                    curl_ops = curl_header.curl_ops
                    curl_log = curl_header.curl_log
                    curl_ops += ['-H', 'Content-Type: multipart/form-data', '-F', 'foldername={0}'.format(new_dir)]
                    curl_ops += ['{0}{1}'.format(self.host_url, self.octoprint_api_path)]
                    if self.log_level != 'QUITE':
                        curl_log += ['-H', 'Content-Type: multipart/form-data', '-F', 'foldername={0}'.format(new_dir)]
                        curl_log += ['{0}{1}'.format(self.host_url, self.octoprint_api_path)]
                    check_dir_output = SP.curl_check_call(ops = curl_ops, log_ops = curl_log)
                    return check_dir_output
                else:
                    dir_path = ''
                    new_dir = dir[1]
                    curl_header = self.return_curl_header_lists()
                    curl_ops = curl_header.curl_ops
                    curl_log = curl_header.curl_log
                    curl_ops += ['-H', 'Content-Type: multipart/form-data', '-F', 'foldername={0}'.format(new_dir)]
                    curl_ops += ['{0}{1}'.format(self.host_url, self.octoprint_api_path)]
                    if self.log_level != 'QUITE':
                        curl_log += ['-H', 'Content-Type: multipart/form-data', '-F', 'foldername={0}'.format(new_dir)]
                        curl_log += ['{0}{1}'.format(self.host_url, self.octoprint_api_path)]
                    check_dir_output = SP.curl_check_call(ops = curl_ops, log_ops = curl_log)
                    return check_dir_output
            exsistent_dirs += check_dir
        # After all that, return the directory path checked/made
        return path

    # Returns parsed json to dictionary from: json.load(json_file)
    @staticmethod
    def return_file_listing_dict_json(json_file_path = None):
        """
        # Copy/paste-able block
        parsed_json = OctoPrint.return_file_listing_dict_json(json_file_path = None)
        """
        if not os.path.exists(json_file_path):
            raise Exception('Could not find json file: {0}'.format(json_file_path))
        #BLDR = Blender
        #json_file_obj = BLDR.import_text(path = json_file_path)
        #parsed_json = json.load(json_file_obj)
        #return parsed_json
        with open(json_file_path) as json_file:
            parsed_json = json.load(json_file)
        return parsed_json

    @staticmethod
    def print_space_statistics(json_dict = None):
        if json_dict is None:
            raise Exception('No JSON dictionary passed to OctoPrint.print_space_statistics staticmethod')
        print('# Printing Server Space Statistics')
        print('## Free space ##', json_dict['free'])
        print('## Used space ##', json_dict['total'])

    @staticmethod
    def print_folders(folders = None):
        if folders is None:
            raise Exception('No Folders passed to OctoPrint.print_folders staticmethod')
        print('# Printing Folder Information')
        for item in folders:
            print('## Refs Resource:', item['refs']['resource'])
            print('## Mount:', item['origin'])
            print('## Type:', item['type'])
            print('## Name:', item['name'])
            print('## Display', item['display'])
            print('## Path:', item['path'])
            print('## Type Path:', item['typePath'])

    @staticmethod
    def print_machinecode_files(machinecode_files = None):
        if machinecode_files is None:
            raise Exception('No Machinecode Files passed to OctoPrint.print_machinecode_files staticmethod')
        print('# Printing Machinecode Files')
        for item in machinecode_files:
            print('## Refs Resource:', item['refs']['resource'])
            print('## Refs Download:', item['refs']['download'])
            print('## Mount:', item['origin'])
            print('## Type:', item['type'])
            print('## Size:', item['size'])
            print('## Name:', item['name'])
            print('### GCode Analysis Filament:', item['gcodeAnalysis']['filament'])
            for count, tool in enumerate(item['gcodeAnalysis']['filament']):
                print('#### Tool #{0}'.format(count))
                print('#### Length:', item['gcodeAnalysis']['filament'][tool]['length'])
                print('#### Volume:', item['gcodeAnalysis']['filament'][tool]['volume'])
            print('#### Dimensions Depth:', item['gcodeAnalysis']['dimensions']['depth'])
            print('#### Dimensions Height:', item['gcodeAnalysis']['dimensions']['height'])
            print('#### Dimensions Width:', item['gcodeAnalysis']['dimensions']['width'])
            print('#### Printing Area Max Y:', item['gcodeAnalysis']['printingArea']['maxY'])
            print('#### Printing Area Min Y:', item['gcodeAnalysis']['printingArea']['minY'])
            print('#### Printing Area Max X:', item['gcodeAnalysis']['printingArea']['maxX'])
            print('#### Printing Area Min X:', item['gcodeAnalysis']['printingArea']['minX'])
            print('#### Printing Area Max Z:', item['gcodeAnalysis']['printingArea']['maxZ'])
            print('#### Printing Area Min Z:', item['gcodeAnalysis']['printingArea']['minZ'])
            print('#### Estimated Print Time:', item['gcodeAnalysis']['estimatedPrintTime'])
            print('## Display', item['display'])
            print('## Path:', item['path'])
            print('## Type Path:', item['typePath'])

    @staticmethod
    def print_model_files(model_files = None):
        if model_files is None:
            raise Exception('No Model Files passed to OctoPrint.print_model_files staticmethod')
        print('# Printing Model Files')
        for item in model_files:
            print('## Refs Resource:', item['refs']['resource'])
            print('## Refs Download:', item['refs']['download'])
            print('## Mount:', item['origin'])
            print('## Type:', item['type'])
            print('## Size:', item['size'])
            print('## Name:', item['name'])
            print('## Hash:', item['hash'])
            print('## Date:', item['date'])
            print('## Display', item['display'])
            print('## Path:', item['path'])
            print('## Type Path:', item['typePath'])


class Os(object):
    """
    # This class contains staticmethods for opertating system level commands used by this addon.
    #  At this point that would be making & deleting directories, removing temporary files,
    #  and checking if a file exsists on disk.
    """
    def __init__(self):
        pass

    # Returns file or directory path provided or 'False' if path does not exsist
    @staticmethod
    def path_exists(path=None):
        """
        # Copy/paste-able block
        Os.path_exists(path = None)
        """
        if path is None:
            raise Exception('No path to check supplied to Os.path_exists(path = "?")')
        path_exists_output = os.path.exists(path)
        if path_exists_output:
            return_output = path
        else:
            return_output = path_exists_output
        print('# Os.path_exists returning: {0}'.format(return_output))
        return return_output

    # Returns output of os.makedirs(dir_path) or False if directory already exists
    @staticmethod
    def mkdir(path=''):
        """
        # Copy/paste-able block
        Os.mkdir(path = None)
        """
        dir_path = Os.path_exists(path = path)
        if dir_path is False:
            mkdir_output = os.makedirs(dir_path)
            return_output = dir_path
        else:
            return_output = False
        print('# Os.mkdir returning: {0}'.format(return_output))
        return return_output

    #  Returns 'False' if no file at path else returns 'path' after issuing: os.remove(path)
    @staticmethod
    def rm_file(path=''):
        """
        # Copy/paste-able block

        """
        if Os.path_exists(path = path):
            # Returns 'None' if pass, else throws an error
            os.remove(path)
            return_output = path
        else:
            return_output = False
        print('# Os.rm_path returning: {0}'.format(return_output))
        return return_output

    #  Returns 'False' if no file at path else returns 'path' after issuing: os.removedirs(path)
    @staticmethod
    def rm_dir(path=''):
        """
        # Copy/paste-able block

        """
        if Os.path_exists(path = path):
            # Returns 'None' if pass, else throws an error
            os.removedirs(path)
            return_output = path
        else:
            return_output = False
        print('# Os.rm_dir returning:{0}'.format(return_output))
        return return_output


class Repetier(object):
    """docstring for Repetier"""
    def __init__(self, context=bpy.context):
        # super Repetier, self).__init__()
        # self.arg = arg
        # Repetier related settings
        self.selected_objects = context.selected_objects
        self.log_level = context.scene.log_level
        # Connection settings
        self.repetier_host = context.scene.repetier_host
        self.repetier_port = context.scene.repetier_port
        self.repetier_user = context.scene.repetier_user
        self.repetier_pass = context.scene.repetier_pass
        self.repetier_x_api_key = context.scene.repetier_x_api_key
        self.repetier_api_path = context.scene.repetier_api_path
        self.repetier_new_dir = context.scene.repetier_new_dir
        # Where to save uploaded files to
        #self.repetier_save_stl_dir = context.scene.repetier_save_stl_dir
        self.repetier_save_gcode_dir = context.scene.repetier_save_gcode_dir
        # Server file & directory listing settings
        #self.repetier_target_search_dir = context.scene.repetier_target_search_dir
        self.repetier_temp_dir = context.scene.repetier_temp_dir
        #
        if context.scene.repetier_port:
            self.host_url = context.scene.repetier_host + ':' + context.scene.repetier_port
        else:
            self.host_url = context.scene.repetier_host

    def return_curl_header_lists(self):
        output = Formatted_output()
        curl_ops = ['-f', '-k', '--connect-timeout', '15']
        curl_log = []
        if self.log_level != 'QUITE':
            curl_log.extend(curl_ops)
        if self.repetier_x_api_key:
            curl_ops += ['-H', 'x-api-key: {0}'.format(self.repetier_x_api_key)]
            if self.log_level == 'VERBOSE':
                curl_log += ['-H', 'x-api-key: {0}'.format(self.repetier_x_api_key)]
            elif self.log_level == 'SCRUBBED':
                curl_log += ['-H', 'x-api-key: X-API-KEY']
        if self.repetier_user and self.repetier_pass:
            curl_ops += ['-u', '{0}:{1}'.format(self.repetier_user, self.repetier_pass)]
            if self.log_level == 'VERBOSE':
                curl_log += ['-u', '{0}:{1}'.format(self.repetier_user, self.repetier_pass)]
            elif self.log_level == 'SCRUBBED':
                curl_log += ['-u', 'USER:PASS']
        output.curl_ops = curl_ops
        output.curl_log = curl_log
        return output

    def upload_gcode(self, gcode_path=''):
        SP = SubProcess()
        file_name = bpy.path.basename(gcode_path)
        curl_header = self.return_curl_header_lists()
        curl_ops = curl_header.curl_ops
        curl_log = curl_header.curl_log
        curl_ops += ['-i', '-X', 'POST', 'Content-Type: multipart/form-data', '-F', '"a=upload"']
        curl_ops += ['-F', 'filename=@{0}'.format(gcode_path), '{0}{1}/{2}'.format(self.host_url, self.repetier_api_path, self.repetier_save_gcode_dir)]
        if self.log_level != 'QUITE':
            curl_log += ['-i', '-X', 'POST', 'Content-Type: multipart/form-data', '-F', '"a=upload"']
            curl_log += ['-F', 'filename=@{0}'.format(gcode_path), '{0}{1}/{2}'.format(self.host_url, self.repetier_api_path, self.repetier_save_gcode_dir)]
        upload_gcode_output = SP.curl_check_call(ops = curl_ops, log_ops = curl_log)
        return upload_gcode_output


class Selected_objects(object):
    def __init__(self, context=bpy.context):
        self.selected_objects = context.selected_objects
        self.preferred_local_slicer = context.scene.preferred_local_slicer
        # Export STL settings
        self.export_stl_directory = context.scene.export_stl_directory
        self.clean_temp_stl_files = context.scene.clean_temp_stl_files
        # Import OBJ settings
        self.import_obj_directory = context.scene.import_obj_directory
        self.clean_temp_obj_files = context.scene.clean_temp_obj_files
        #
        self.export_stl_treat_selected_as = context.scene.export_stl_treat_selected_as
        self.slic3r_repaired_parent_name = context.scene.slic3r_repaired_parent_name
        #
        self.slic3r_gcode_directory = context.scene.slic3r_gcode_directory
        self.slic3r_preview_gcode = context.scene.slic3r_preview_gcode
        #
        self.curaengine_gcode_directory = context.scene.curaengine_gcode_directory
        self.curaengine_preview_gcode = context.scene.curaengine_preview_gcode
        #
        self.octoprint_auto_upload_from_slicers = context.scene.octoprint_auto_upload_from_slicers
        self.repetier_auto_upload_from_slicers = context.scene.repetier_auto_upload_from_slicers
        self.open_browser_after_upload = context.scene.open_browser_after_upload
        if context.scene.open_browser_after_upload is True and 'Repetier' in context.scene.preferred_print_server:
            if context.scene.repetier_port:
                self.server_url = context.scene.repetier_host + ':' + context.scene.repetier_port
            else:
                self.server_url = context.scene.repetier_host
        if context.scene.open_browser_after_upload is True and 'OctoPrint' in context.scene.preferred_print_server:
            if context.scene.octoprint_port:
                self.server_url = context.scene.octoprint_host + ':' + context.scene.octoprint_port
            else:
                self.server_url = context.scene.octoprint_host

    # Returns output of export_stl(stl_path = stl_path, objects = object)
    def export_as_stl(self, context=bpy.context):
        # Initialize objects for calling class methods
        BLDR = Blender(context)
        operation_output = Formatted_output()
        # Make output directory if needed, output will either be 'False' if directory did not need
        #  to be made or the value of 'path' if the directory is new and made, or will error out if
        #  path cannot be made.
        operation_output.mkdir_output = Os.mkdir(path = self.export_stl_directory)
        if 'Individual' in self.export_stl_treat_selected_as or 'Merge' in self.export_stl_treat_selected_as:
            export_stl_output = []
            for obj in self.selected_objects:
                stl_path = os.path.join(self.export_stl_directory, obj.name + '.stl')
                # Export objects as STL
                operation_output.blender_export_stl_output += [BLDR.export_stl(stl_path = stl_path, objects = obj)]
        else:
            if bpy.data.is_saved is True:
                stl_path = os.path.join(self.export_stl_directory, bpy.path.basename(bpy.context.blend_data.filepath) + '.stl')
            else:
        	    stl_path = os.path.join(self.export_stl_directory, 'Untitled' + '.stl')
            # Export objects as STL
            operation_output.blender_export_stl_output = BLDR.export_stl(stl_path = stl_path, objects = self.selected_objects)
        # Return output object of what just happened
        return operation_output

    #
    def repair_through_slic3r(self, context=bpy.context):
        if not self.selected_objects:
            raise Exception('Please select some objects first.')
        # Initialize objects for calling class methods
        BLDR = Blender(context)
        SLCR = Slic3r(context)
        operation_output = Formatted_output()
        # Empty values for operation_output for this run
        operation_output.mkdir_output = []
        operation_output.blender_export_stl_output = []
        operation_output.slic3r_repair_stl_output = []
        operation_output.blender_imported_objects = []
        operation_output.rm_file_output = []
        # Make output directory if needed, output will either be 'False' if directory did not need
        #  to be made or the value of 'path' if the directory is new and made, or will error out if
        #  path cannot be made.
        operation_output.mkdir_output += [Os.mkdir(path = self.export_stl_directory)]
        operation_output.mkdir_output += [Os.mkdir(path = self.import_obj_directory)]
        # Either export, repair & re-import individual files (per object) or the whole scene as one file
        if 'Individual' in self.export_stl_treat_selected_as or 'Merge' in self.export_stl_treat_selected_as:
            print('## Inidvidual or Merge export settings detected ##')
            for c, obj in enumerate(self.selected_objects):
                stl_path = os.path.join(self.export_stl_directory, obj.name + '.stl')
                obj_path = os.path.join(self.import_obj_directory, obj.name + '_fixed.obj')
                # Export
                operation_output.blender_export_stl_output += [BLDR.export_stl(stl_path = stl_path, objects = obj)]
                if operation_output.blender_export_stl_output[c]:
                    # Repair
                    operation_output.slic3r_repair_stl_output += [SLCR.repair_stl(stl_path = operation_output.blender_export_stl_output[c])]
                    # Import
                    imported_object = BLDR.import_obj(path = obj_path)
                    # Append imported object to list for latter outputting
                    operation_output.blender_imported_objects += [imported_object]
                    # Parent to named empty
                    parent_to_named_empty_output = Blender.parent_object_to_named_empty(empty_name = self.slic3r_repaired_parent_name, empty_location=(0, 0, 0), child_object = imported_object)
                    # Clean up temp STL & OBJ files if enabled
                    if self.clean_temp_stl_files is True:
                        operation_output.rm_file_output += [Os.rm_file(path = stl_path)]
                    if self.clean_temp_obj_files is True:
                        operation_output.rm_file_output += [Os.rm_file(path = obj_path)]
        else:
            print('## Batch or Scene export settings detected ##')
            if bpy.data.is_saved is True:
                stl_path = os.path.join(self.export_stl_directory, bpy.path.basename(bpy.context.blend_data.filepath) + '.stl')
                obj_path = os.path.join(self.import_obj_directory, bpy.path.basename(bpy.context.blend_data.filepath) + '_fixed.obj')
            else:
        	    stl_path = os.path.join(self.export_stl_directory, 'Untitled.stl')
        	    obj_path = os.path.join(self.import_obj_directory, 'Untitled_fixed.obj')
            # Export
            operation_output.blender_export_stl_output += [BLDR.export_stl(stl_path = stl_path, objects = self.selected_objects)]
            if operation_output.blender_export_stl_output[0]:
                # Repair
                operation_output.slic3r_repair_stl_output += [SLCR.repair_stl(stl_path = operation_output.blender_export_stl_output[0])]
                # Import
                imported_object = BLDR.import_obj(path = obj_path)
                operation_output.blender_imported_objects = imported_object
                # Parent to named empty
                parent_to_named_empty_output = Blender.parent_object_to_named_empty(empty_name = self.slic3r_repaired_parent_name, empty_location=(0, 0, 0), child_object = imported_object)
                # Clean up temp STL & OBJ files if enabled.
                if self.clean_temp_stl_files is True:
                    operation_output.rm_file_output += [Os.rm_file(path = stl_path)]
                if self.clean_temp_obj_files is True:
                    operation_output.rm_file_output += [Os.rm_file(path = obj_path)]
        # Return output object of what just happened
        return operation_output

    #
    def local_slicer(self, context=bpy.context):
        # Initialize objects for calling class methods
        BLDR = Blender(context)
        if self.preferred_local_slicer == 'Slic3r':
            SLCR = Slic3r(context)
            gcode_dir = self.slic3r_gcode_directory
        elif self.preferred_local_slicer == 'CuraEngine':
            SLCR = CuraEngine(context)
            gcode_dir = self.curaengine_gcode_directory
        operation_output = Formatted_output()
        # Empty values for operation_output for this run
        operation_output.mkdir_output = []
        operation_output.blender_export_stl_output = []
        operation_output.slice_stl_output = []
        operation_output.blender_imported_texts = []
        operation_output.rm_file_output = []
        # Make output directory if needed, output will either be 'False' if directory did not need
        #  to be made or the value of 'path' if the directory is new and made, or will error out if
        #  path cannot be made.
        operation_output.mkdir_output += [Os.mkdir(path = self.export_stl_directory)]
        operation_output.mkdir_output += [Os.mkdir(path = gcode_dir)]
        # Either export, repair & re-import individual files (per object) or the whole scene as one file
        if 'Individual' in self.export_stl_treat_selected_as:
            print('## Individual export settings detected ##')
            stl_file_list = []
            for c, obj in enumerate(self.selected_objects):
                stl_path = os.path.join(self.export_stl_directory, obj.name + '.stl')
                gcode_path = os.path.join(gcode_dir, obj.name + '.gcode')
                # Export
                operation_output.blender_export_stl_output += [BLDR.export_stl(stl_path = stl_path, objects = obj)]
                if operation_output.blender_export_stl_output[c]:
                    # Slice
                    operation_output.slice_stl_output += [SLCR.slice_stl(stl_path = operation_output.blender_export_stl_output[c], gcode_path = gcode_path)]
                    stl_file_list += [operation_output.blender_export_stl_output]
                    if self.slic3r_preview_gcode is True:
                        # Import & Append imported object to list for latter outputting
                        operation_output.blender_imported_texts += [Blender.import_text(path = gcode_path)]
                    # Upload outputed GCode to servers if enabled
                    if self.octoprint_auto_upload_from_slicers is True:
                        print('# Uploading file: {0} to OctoPrint server'.format(gcode_path))
                        OP = OctoPrint(context)
                        OP.upload_file(gcode_path = gcode_path)
                    if self.repetier_auto_upload_from_slicers is True:
                        print('# Uploading file: {0} to Repetier server'.format(gcode_path))
                        RP = Repetier(context)
                        RP.upload_gcode(gcode_path = gcode_path)
                # Clean up temp STL & OBJ files if enabled
                if self.clean_temp_stl_files is True:
                    operation_output.rm_file_output += [Os.rm_file(path = stl_path)]
            if self.open_browser_after_upload is True:
                Blender.open_browser(url = self.server_url)
        elif 'Merge' in self.export_stl_treat_selected_as:
            print('## Merge export settings detected ##')
            if bpy.data.is_saved is True:
                gcode_path = os.path.join(gcode_dir, bpy.path.basename(bpy.context.blend_data.filepath) + '.gcode')
            else:
        	    gcode_path = os.path.join(gcode_dir, 'Untitled.gcode')
            for obj in self.selected_objects:
                stl_path = os.path.join(self.export_stl_directory, obj.name + '.stl')
                # Export
                operation_output.blender_export_stl_output += [BLDR.export_stl(stl_path = stl_path, objects = obj)]
            if operation_output.blender_export_stl_output:
                # Slice
                operation_output.slice_stl_output += [SLCR.slice_stl(stl_path = operation_output.blender_export_stl_output, gcode_path = gcode_path)]
                if self.slic3r_preview_gcode is True:
                    # Import text object
                    operation_output.blender_imported_texts = Blender.import_text(path = gcode_path)
                # Upload outputed GCode to servers if enabled
                if self.octoprint_auto_upload_from_slicers is True:
                    print('# Uploading file: {0} to OctoPrint server'.format(gcode_path))
                    OP = OctoPrint(context)
                    OP.upload_file(gcode_path = gcode_path)
                if self.repetier_auto_upload_from_slicers is True:
                    print('# Uploading file: {0} to Repetier server'.format(gcode_path))
                    RP = Repetier(context)
                    RP.upload_gcode(gcode_path = gcode_path)
            if self.clean_temp_stl_files is True:
                # Clean up temp STL & OBJ files if enabled
                for obj in self.selected_objects:
                    operation_output.rm_file_output += [Os.rm_file(path = stl_path)]
            if self.open_browser_after_upload is True:
                Blender.open_browser(url = self.server_url)
        else:
            print('## Batch export settings detected ##')
            if bpy.data.is_saved is True:
                stl_path = os.path.join(self.export_stl_directory, bpy.path.basename(bpy.context.blend_data.filepath) + '.stl')
                gcode_path = os.path.join(gcode_dir, bpy.path.basename(bpy.context.blend_data.filepath) + '.gcode')
            else:
        	    stl_path = os.path.join(self.export_stl_directory, 'Untitled.stl')
        	    gcode_path = os.path.join(gcode_dir, 'Untitled.gcode')
            # Export
            operation_output.blender_export_stl_output += [BLDR.export_stl(stl_path = stl_path, objects = self.selected_objects)]
            if operation_output.blender_export_stl_output[0]:
                # Slice
                operation_output.slice_stl_output += [SLCR.slice_stl(stl_path = operation_output.blender_export_stl_output[0], gcode_path = gcode_path)]
            if self.slic3r_preview_gcode is True:
                # Import
                operation_output.blender_imported_texts = Blender.import_text(path = gcode_path)
            # Upload outputed GCode to servers if enabled
            if self.octoprint_auto_upload_from_slicers is True:
                print('# Uploading file: {0} to OctoPrint server'.format(gcode_path))
                OP = OctoPrint(context)
                OP.upload_file(gcode_path = gcode_path)
            if self.repetier_auto_upload_from_slicers is True:
                print('# Uploading file: {0} to Repetier server'.format(gcode_path))
                RP = Repetier(context)
                RP.upload_gcode(gcode_path = gcode_path)
            # Clean up temp STL & OBJ files if enabled.
            if self.clean_temp_stl_files is True:
                operation_output.rm_file_output += [Os.rm_file(path = stl_path)]
            if self.open_browser_after_upload is True:
                Blender.open_browser(url = self.server_url)
        # Return output object of what just happened
        return operation_output


class Slic3r(object):
    """
    # This class contains short-cuts to slicer repair & slice operations
    """
    def __init__(self, context=bpy.context):
        self.selected_objects = context.selected_objects
        # Slic3r panel settings for this instance
        self.slic3r_exec_dir = context.scene.slic3r_exec_dir
        self.slic3r_exec_name = context.scene.slic3r_exec_name
        self.slic3r_conf_path = context.scene.slic3r_conf_path
        self.slic3r_post_script = context.scene.slic3r_post_script
        self.slic3r_extra_args = context.scene.slic3r_extra_args
        self.slic3r_repaired_parent_name = context.scene.slic3r_repaired_parent_name
        self.slic3r_gcode_directory = context.scene.slic3r_gcode_directory
        #
        self.export_stl_treat_selected_as = context.scene.export_stl_treat_selected_as

    # Raises exception if 'stl_path' does not exists, else returns output of SP.slic3r_check_call(ops = ['--repair', path])
    def repair_stl(self, stl_path=''):
        SP = SubProcess()
        path = Os.path_exists(path = stl_path)
        if path is False:
            raise Exception('No STL file supplied for Slic3r to repair')
        repair_output = SP.slic3r_check_call(ops = ['--repair', path])
        print("# Slic3r.repair_stl returning output of: SP.slic3r_check_call(ops = ['--repair', {0}])".format(path))
        return repair_output

    # Raises exception if 'stl_path' or 'gcode_path' does not exists, else returns output of SP.slic3r_check_call(ops = args)
    def slice_stl(self, stl_path=None, gcode_path=None):
        SP = SubProcess()
        if gcode_path is None:
            raise Exception('No GCODE output file path supplied for Slic3r')
        if isinstance(stl_path, list):
            path = []
            for p in stl_path:
                path += [Os.path_exists(path = p)]
        elif stl_path:
            path = Os.path_exists(path = stl_path)
        else:
            path = False
        if path is False:
            raise Exception('No STL input file(s) supplied for Slic3r')
        args = []
        if os.path.exists(self.slic3r_conf_path):
            args += ['--load', self.slic3r_conf_path]
        args += ['--output', gcode_path]
        if os.path.exists(self.slic3r_post_script):
            args += ['--post-process', self.slic3r_post_script]
        if self.slic3r_extra_args:
            extra_args = []
            for arg in enumerate(self.slic3r_extra_args.split(' ')):
                extra_args += [arg[1]]
            args.extend(extra_args)
        if 'Merge' in self.export_stl_treat_selected_as:
            args += ['--merge']
            args.extend(path)
        else:
            args += [path]
        slice_stl_output = SP.slic3r_check_call(ops = args)
        print('# Slic3r.slic3r_slice_stl returning output of: SP.slic3r_check_call(ops = {0})'.format(args))
        return slice_stl_output


class SubProcess(object):
    """
    # This class holds short-custs to Slic3r, CuraEngin and Curl subprocess.check_call([exce_path, arg])
    """
    def __init__(self, context=bpy.context):
        # super SubProcess, self).__init__()
        # self.arg = arg
        if os.path.exists(os.path.join(context.scene.slic3r_exec_dir, context.scene.slic3r_exec_name)):
            self.slic3r_exec_path = os.path.join(context.scene.slic3r_exec_dir, context.scene.slic3r_exec_name)
        else:
            self.slic3r_exec_path = context.scene.slic3r_exec_name
        if os.path.exists(os.path.join(context.scene.curaengine_exec_dir, context.scene.curaengine_exec_name)):
            self.curaengine_exec_path = os.path.join(context.scene.curaengine_exec_dir, context.scene.curaengine_exec_name)
        else:
            self.curaengine_exec_path = context.scene.curaengine_exec_name
        if os.path.exists(os.path.join(context.scene.curl_exec_dir, context.scene.curl_exec_name)):
            self.curl_exec_path = os.path.join(context.scene.curl_exec_dir, context.scene.curl_exec_name)
        else:
            self.curl_exec_path = context.scene.curl_exec_name

    # Returns '0' or errors out upon calling Slic3r with provided arguments
    def slic3r_check_call(self, ops=[]):
        if not ops:
            raise Exception('No options supplied for Slic3r')
        slic3r_ops = [self.slic3r_exec_path]
        slic3r_ops.extend(ops)
        slic3r_output = subprocess.check_call(slic3r_ops)
        print('# Returning output of: SubProcess.slic3r_check_call({0})'.format(slic3r_ops))
        return slic3r_output

    # Returns '0' or errors out upon calling CuraEngine with provided arguments
    def curaengine_check_call(self, ops=[]):
        if not ops:
            raise Exception('No options supplied for Slic3r')
        curaengine_ops = [self.curaengine_exec_path]
        curaengine_ops.extend(ops)
        curaengine_output = subprocess.check_call(curaengine_ops)
        print('# Returning output of: SubProcess.curaengine_check_call({0})'.format(curaengine_ops))
        return curaengine_output

    def curl_check_call(self, ops=[], log_ops=[]):
        if not ops:
            raise Exception('No options supplied for curl')
        curl_array = [self.curl_exec_path]
        curl_array.extend(ops)
        if log_ops:
            curl_log = [self.curl_exec_path]
            curl_log.extend(log_ops)
            print('# Using subprocess.checkcall({0})'.format(curl_log))
        curl_check_call_output = subprocess.check_call(curl_array)
        return curl_check_call_output

    def curl_getoutput(self, ops = None):
        if not ops:
            raise Exception('No options supplied for curl')
        curl_args = self.curl_exec_path
        curl_args += ' ' + ops
        curl_log = curl_args
        print('# Using subprocess.getoutput({0})'.format(curl_log))
        curl_getoutput_output = subprocess.getoutput(curl_args)
        return curl_getoutput_output


class Webcam(object):
    """docstring for Webcam"""
    def __init__(self, context=bpy.context):
        # super Webcam, self).__init__()
        # self.arg = arg
        # Webcam related settings
        self.log_level = context.scene.log_level
        self.button_text_color = context.scene.button_text_color
        self.button_background_color = context.scene.button_background_color
        if 'OctoPrint' in context.scene.preferred_print_server:
            self.snapshot_name = context.scene.octoprint_snapshot_name
            self.preview_xy_scale = context.scene.octoprint_preview_xy_scale
            self.preview_placement = context.scene.octoprint_preview_placement
            self.preview_layer = context.scene.octoprint_preview_layer
            self.target_screen = context.scene.octoprint_target_screen
            self.target_3dview = context.scene.octoprint_target_3dview
            #
            self.camera_port = context.scene.octoprint_camera_port
            self.camera_host = context.scene.octoprint_host
            self.snapshot_action = context.scene.octoprint_snapshot_action
            self.stream_action = context.scene.octoprint_stream_action
            self.temp_dir = context.scene.octoprint_temp_dir
            self.snapshot_name = context.scene.octoprint_snapshot_name
            self.preview_placement = context.scene.octoprint_preview_placement
            self.preview_layer = context.scene.octoprint_preview_layer
            self.preview_xy_scale = context.scene.octoprint_preview_xy_scale
            self.user = context.scene.octoprint_user
            self.passphrase = context.scene.octoprint_pass
        elif 'Repetier' in context.scene.preferred_print_server:
            self.snapshot_name = context.scene.repetier_snapshot_name
            self.preview_xy_scale = context.scene.repetier_preview_xy_scale
            self.preview_placement = context.scene.repetier_preview_placement
            self.preview_layer = context.scene.repetier_preview_layer
            self.target_screen = context.scene.repetier_target_screen
            self.target_3dview = context.scene.repetier_target_3dview
            #
            self.camera_port = context.scene.repetier_camera_port
            self.camera_host = context.scene.repetier_host
            self.snapshot_action = context.scene.repetier_snapshot_action
            self.stream_action = context.scene.repetier_stream_action
            self.temp_dir = context.scene.repetier_temp_dir
            self.snapshot_name = context.scene.repetier_snapshot_name
            self.preview_placement = context.scene.repetier_preview_placement
            self.preview_layer = context.scene.repetier_preview_layer
            self.preview_xy_scale = context.scene.repetier_preview_xy_scale
            self.user = context.scene.repetier_user
            self.passphrase = context.scene.repetier_pass
        if self.camera_port:
            self.snapshot_url = self.camera_host + ':' + self.camera_port + '/' + self.snapshot_action
            self.stream_url = self.camera_host + ':' + self.camera_port + '/' + self.stream_action
        else:
            self.snapshot_url = self.camera_host + '/' + self.snapshot_action
            self.stream_url = self.camera_host + '/' + self.stream_action

    def download_snapshot(self):
        """
        # Returns download_file_path unless runnning: SP.curl_check_call(ops = curl_ops, log_ops = curl_log)
        #  errors out.
        """
        SP = SubProcess()
        download_file_path = os.path.join(self.temp_dir, self.snapshot_name + '.jpg')
        curl_ops = ['-k', '--connect-timeout', '15']
        curl_log = []
        if self.log_level != 'QUITE':
            curl_log.extend(curl_ops)
        if self.user and self.passphrase:
            curl_ops += ['-u', '{0}:{1}'.format(self.user, self.passphrase)]
            if self.log_level == 'VERBOSE':
                curl_log += ['-u', '{0}:{1}'.format(self.user, self.passphrase)]
            elif self.log_level == 'SCRUBBED':
                curl_log += ['-u', 'USER:PASS']
        curl_ops += ['-o', download_file_path, self.snapshot_url]
        if self.log_level == 'VERBOSE':
            curl_log += ['-o', download_file_path, self.snapshot_url]
        elif self.log_level == 'SCRUBBED':
            curl_log += ['-o', 'DOWNLOAD_PATH', 'URL']
        download_snapshot_output = SP.curl_check_call(ops = curl_ops, log_ops = curl_log)
        return download_file_path

    def add_view_plane(self, image_name='', object_name='', material_name='', texture_name='', x_dimension='', y_dimension='', xy_scale=''):
        """
        # Copy / paste-able block
        WC = Webcam(context)
        WC.add_view_plane(image_name = self.snapshot_name+'.jpg', object_name='', material_name='', texture_name='', x_dimension='', y_dimension='', xy_scale='')
        # Returns output of Blender.get_object_by_name(object_name = object_name)
        #  after attempting to setup an object (default: Plane) with an image texture
        """
        # BLDR = Blender
        obj = Blender.get_object_by_name(object_name = object_name)
        if obj is None:
            obj = Blender.new_plane(name = object_name, layers = self.preview_layer)
        if obj is None:
            raise Exception('Could not create/target correct preview plane')
        obj_dims = obj.dimensions
        obj.dimensions = x_dimension/self.preview_xy_scale, y_dimension/self.preview_xy_scale, obj_dims[2]
        if 'NORTH' in self.preview_placement:
            obj.location[1] = obj.dimensions[1]/2
        elif 'EAST' in self.preview_placement:
            obj.location[0] = obj.dimensions[0]/2
        elif 'SOUTH' in self.preview_placement:
            obj.location[1] = -obj.dimensions[1]/2
        elif 'WEST' in self.preview_placement:
            obj.location[0] = -obj.dimensions[0]/2
        materialize_object_output = self.materialize_object(material_name = material_name, object = obj, diffuse_color = [0, 0, 0], use_shadeless = True)
        obj_mat = materialize_object_output.data.materials.get(material_name)
        #obj_mat = obj.data.materials.get(material_name)
        tex = bpy.data.textures.get(texture_name)
        if tex is None:
            tex = bpy.data.textures.new(texture_name, 'IMAGE')
        mat = bpy.data.materials.get(material_name)
        mat_slots = mat.texture_slots.get(texture_name)
        if mat_slots is None:
            mat_slots = mat.texture_slots.add()
        mat_slots.texture = tex
        tex.image = bpy.data.images[image_name]
        obj.data.materials[material_name].texture_slots[texture_name].texture_coords = 'ORCO'
        # Update object if this is not the first time the preview/stream button has been pressed
        materialize_object_output.data.update()
        #bpy.data.objects[object_name].data.update()
        # Update the scene to all the changes required to view an image on a plane within Blender
        bpy.context.scene.update()
        return obj

    def modify_viewport_3dview(self, animate=''):
        """
        # Copy / paste-able block
        WC = Webcam(context)
        WC.modify_viewport_3dview(animate = True)
        # Updates a texture image or starts BGE to enable streaming if 'animate' is True
        #  the 'self.target_screen' targets a specific UI screen, for example 'Default'
        #  the 'self.target_3dview' targets a specific 3D View port within that screen
        #  and the 'self.preview_layer' targets a specific layer to show on that view port.
        """
        viewport_shade='TEXTURED'
        bpy.context.scene.render.engine = Target_render_engine
        bpy.context.scene.game_settings.material_mode = Target_material_mode
        areas = bpy.data.screens[self.target_screen].areas
        for area in areas:
            if area.type == 'VIEW_3D':
                bpy.ops.object.mode_set(mode='OBJECT')
                override = bpy.context.copy()
                override['area'] = area
                for counter, space in enumerate(area.spaces):
                    if space.type == 'VIEW_3D' and self.target_3dview == counter:
                        space.viewport_shade = Target_viewport_shade
                        for count, layer in enumerate(space.layers):
                            if count != self.preview_layer:
                                layer = False
                            else:
                                layer = True
                if animate == True:
                    bpy.ops.view3d.game_start()
                    break

    def import_local_image(self, filename='', directory=''):
        """
        # Copy / paste-able block
        WC = Webcam(context)
        img = WC.import_local_image(filename='', directory='')
        # Returns imported image else if image already exsists reloads from disk
        # Note if using this for texturing an object the texture still will need to
        #  refresh itself, for example: bpy.data.objects[object_name].data.update()
        """
        img = bpy.data.images.get(filename)
        if img is None:
            bpy.data.images.load(os.path.join(directory, filename))
            bpy.data.images[-1].name = filename
            img = bpy.data.images.get(filename)
        else:
            bpy.data.images[filename].reload()
        return img

    def materialize_object(self, object=None, material_name=None, diffuse_color=None, use_shadeless=True):
        """
        # Copy / paste-able block
        WC = Webcam(context)
        materialize_object_output = WC.materialize_object(object='', material_name = None, diffuse_color = self.button_background_color, use_shadeless=True)
        # Returns the object after applying the following.
        # This adds a color if 'diffuse_color' is not None to a named material and
        #  adds that material to the object
        #  effectively a short cut for bpy.data.materials.new(name=material_name)
        #  and bpy.data.objects.get(object.name).data.materials.append(bpy.data.materials.get(material_name))
        #  with some scripted logic to prevent adding the same material to the same object more than once.
        """
        if object is None:
            raise Exception('No object supplied to materialize')
        if material_name is None:
            material_name = object.name + '_Material'
        # Setup new material if none exists for button text
        mat = bpy.data.materials.get(material_name)
        if mat is None:
            mat = bpy.data.materials.new(name = material_name)
        if diffuse_color is not None:
            # Note by addressing the first three this avoids errors with feeding longer lists
            #  while this will mean that colors between BGE & Textured Object mode
            #  it also means that there will be buttons with visible & customized colors
            mat.diffuse_color = (diffuse_color[0], diffuse_color[1], diffuse_color[2])
        # Assign or update material on button plane
        obj_mat = object.data.materials.get(material_name)
        if obj_mat is None:
            object.data.materials.append(mat)
            obj_mat = object.data.materials.get(material_name)
        else:
            object.data.materials[0] = mat
        object.active_material.use_shadeless = use_shadeless
        return object

    def add_text_button(self, text_name='', text_body='', location=''):
        """
        # Copy / paste-able block
        WC = Webcam(context)
        WC.add_text_button(text_name='', text_body='', location='')
        # This adds text and then scales a new plane behind the text as 'text_name' + '_Plane'
        #  so that other functions can setup button logic for BGE interactions.
        """
        plane_name = text_name + '_Plane'
        plane_material_name = text_name + '_Plane_Material'
        text_material_name = text_name + '_Text_Material'
        # Deselect all meshes
        bpy.ops.object.select_all(action='DESELECT')
        text_obj = bpy.data.objects.get(text_name)
        if text_obj is None:
            layers = Blender.return_layer_list(layer = self.preview_layer)
            bpy.ops.object.text_add(layers = layers)
            bpy.data.objects[-1].name = text_name
            text_obj = bpy.data.objects.get(text_name)
        # Write text_body into object
        text_obj.data.body = text_body
        # Set origin to geometry
        bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='MEDIAN')
        text_obj.location = (text_obj.location[0], text_obj.location[1], location[2])
        text_dimensions = text_obj.dimensions
        # Deselect all meshes
        bpy.ops.object.select_all(action='DESELECT')
        # Add plane under & size it
        plane_obj = bpy.data.objects.get(plane_name)
        if plane_obj is None:
            plane_obj = Blender.new_plane(name = plane_name, layers = self.preview_layer)
        # This next bit scales the background plane to the dimensions of text corner by corner
        # Lower left
        plane_obj.data.vertices[0].co = (-text_dimensions[0]/2, -text_dimensions[1]/2, text_obj.location[2])
        # Lower right
        plane_obj.data.vertices[1].co = (text_dimensions[0]/2, -text_dimensions[1]/2, text_obj.location[2])
        # Upper left
        plane_obj.data.vertices[2].co = (-text_dimensions[0]/2, text_dimensions[1]/2, text_obj.location[2])
        # Upper right
        plane_obj.data.vertices[3].co = (text_dimensions[0]/2, text_dimensions[1]/2, text_obj.location[2])
        # Parent text to plane
        text_obj.parent = plane_obj
        plane_obj.location = (location[0], location[1], location[2]/2)
        text_obj.location = (text_obj.location[0], text_obj.location[1], text_obj.location[2]+0.5)
        # Colorize text & background for while in BGE
        text_obj.color = self.button_text_color
        plane_obj.color = self.button_background_color
        # Assign material to text & background plane for while in textured object mode
        self.materialize_object(material_name = text_material_name, object = text_obj, diffuse_color = self.button_text_color, use_shadeless = True)
        self.materialize_object(material_name = plane_material_name, object = plane_obj, diffuse_color = self.button_background_color, use_shadeless = True)

    def write_bge_script_webcam(self, controller_script_name='', default_image='', video_path=''):
        """
        # Copy / paste-able block
        WC = Webcam(context)
        WC.write_bge_script_webcam(controller_script_name='', default_image='', video_path='')
        # Returns Text Object after writing (or clearing & then writing)
        #  a new BGE controller script for updating an object texture image
        #  with a Webcam stream.
        """
        text_block = bpy.data.texts.get(controller_script_name)
        if text_block is None:
            bpy.ops.text.new()
            bpy.data.texts[-1].name = controller_script_name
            text_block = bpy.data.texts[controller_script_name]
        bpy.data.texts[controller_script_name].clear()
        # Now we can write line by line what should be in here note, new-line feeds are not assumed, eg "\n" is required
        #text_block.write('some text with a new line\n')
        # In this case we are going to write a script for playing video sources onto an object texture in with
        #  Blender Game Engine, however, the following seems to work on Blender version 2.76 or lower
        text_block.write('#!/usr/bin/env python\n')
        text_block.write('import bge\n')
        text_block.write('cont = bge.logic.getCurrentController()\n')
        text_block.write('obj = cont.owner\n')
        text_block.write('def main():\n')
        text_block.write('    if not hasattr(bge.logic, "video"):\n')
        text_block.write('        bge.render.showMouse(True)\n')
        text_block.write('        ID = bge.texture.materialID(obj, "IM{0}")\n'.format(default_image))
        text_block.write('        bge.logic.video = bge.texture.Texture(obj, ID)\n')
        # Note if you are looking to steal this function for another project you may also want the next part
        #  for addressing local webcam hardware too
        # if camera_addr:
        #     text_block.write("        bge.logic.video.source = bge.texture.VideoFFmpeg('{0}', 0)\n".format(camera_addr))
        # elif video_path:
        text_block.write("        bge.logic.video.source = bge.texture.VideoFFmpeg('{0}')\n".format(video_path))
        text_block.write('        bge.logic.video.source.play()\n')
        text_block.write('    bge.logic.video.refresh(True)\n')
        text_block.write('main()')
        return text_block

    def setup_bge_logic_webcam(self, object_name='', sensor_name='', controller_name='', controller_script_name=''):
        """
        # Copy / paste-able block
        WC = Webcam(context)
        WC.setup_bge_logic_webcam(object_name='', sensor_name='', controller_name='', controller_script_name='')
        # This links 'controller_name' & 'sensor_name' with 'controller_script_name' on 'object_name'
        #  such that when BGE plays the script for updating an object texture with a video is fired
        """
        # Set-up game Sensor for object
        vid_obj_sensor = bpy.data.objects[object_name].game.sensors.get(sensor_name)
        if vid_obj_sensor is None:
            bpy.ops.logic.sensor_add(type='ALWAYS', name=sensor_name, object=object_name)
            vid_obj_sensor = bpy.data.objects[object_name].game.sensors.get(sensor_name)
        vid_obj_sensor.use_pulse_true_level = True
        # Set-up game Controller for object
        vid_obj_controller = bpy.data.objects[object_name].game.controllers.get(controller_name)
        if vid_obj_controller is None:
            bpy.ops.logic.controller_add(type='PYTHON', name = controller_name, object = object_name)
            vid_obj_controller = bpy.data.objects[object_name].game.controllers.get(controller_name)
        vid_obj_controller.text = bpy.data.texts[controller_script_name]

        # Link things together
        vid_obj_sensor.link(vid_obj_controller)

    def setup_bge_logic_button(self, object_name='', actuator_type='GAME', actuator_mode='QUIT'):
        """
        # Copy / paste-able block
        WC = Webcam(context)
        WC.setup_bge_logic_button(object_name='', actuator_type='GAME', actuator_mode='QUIT')
        # This sets up BGE logic bricks on 'object_name' for acting like a mouse selectable button
        """
        sensor_click_name = object_name + '_Sensor_Click'
        sensor_mouseover_name = object_name + '_Sensor_Mouse_Over'
        controller_name = object_name + '_Controller'
        actuator_name = object_name + '_Actuator'
        # Make two sensors for mouse events
        click_sensor = bpy.data.objects[object_name].game.sensors.get(sensor_click_name)
        if click_sensor is None:
            print('## Making a click sensor:', sensor_click_name)
            bpy.ops.logic.sensor_add(type='MOUSE', name = sensor_click_name, object = object_name)
            click_sensor = bpy.data.objects[object_name].game.sensors.get(sensor_click_name)
        click_sensor.mouse_event = 'LEFTCLICK'
        mouseover_sensor = bpy.data.objects[object_name].game.sensors.get(sensor_mouseover_name)
        if mouseover_sensor is None:
            print('## Making a mouseover sensor:', sensor_mouseover_name)
            bpy.ops.logic.sensor_add(type='MOUSE', name = sensor_mouseover_name, object = object_name)
            mouseover_sensor = bpy.data.objects[object_name].game.sensors.get(sensor_mouseover_name)
        mouseover_sensor.mouse_event = 'MOUSEOVER'
        ## TO-DO - add mouseover_off_sensor
        ##  for Blender version 2.76 this means the above plus the following
        ##  mouseover_sensor_off.invert = True
        # Make an AND controller, TO-DO inject a BGE python script for controlling more than just logic
        controller = bpy.data.objects[object_name].game.controllers.get(controller_name)
        if controller is None:
            print('## Making a controller:', controller_name)
            bpy.ops.logic.controller_add(type='LOGIC_AND', name = controller_name, object = object_name)
            controller = bpy.data.objects[object_name].game.controllers.get(controller_name)
        ## TO-DO - Inject python script so that buttons can be scaled up & down when mouse hovers & leaves
        ##    bpy.ops.logic.controller_add(type='PYTHON', name = controller_name, object = object_name)
        ##    script = bpy.data.texts.get(script_name)
        ##    controller = bpy.data.objects[object_name].game.controllers.get(controller_name)
        ##    controller.text = script
        # Link the sensors to controller
        click_sensor.link(controller)
        mouseover_sensor.link(controller)
        # Make an actuator
        actuator = bpy.data.objects[object_name].game.actuators.get(actuator_name)
        if actuator is None:
            print('## Making a actuator:', actuator_name)
            bpy.ops.logic.actuator_add(type = actuator_type, name = actuator_name, object = object_name)
            actuator = bpy.data.objects[object_name].game.actuators.get(actuator_name)
        actuator.mode = actuator_mode
        # Link controller to actuator
        actuator.link(controller)

    def init_preview(self, action='snapshot'):
        # Deselect all meshes, perhaps that will keep new textures off preexisting meshes
        bpy.ops.object.select_all(action='DESELECT')

        image_file_name = self.snapshot_name + '.jpg'
        image_plane_name = self.snapshot_name + '_Plane'
        bge_sensor_name = self.snapshot_name + '_Sensor'
        bge_controller_name = self.snapshot_name + '_Controller'
        bge_material_name = self.snapshot_name + '_Material'
        bge_texture_name = self.snapshot_name + '_Texture'
        bge_controller_script_name = self.snapshot_name + '_Script.py'
        snapshot_url = self.snapshot_url
        stream_url = self.stream_url
        # Take a picture of 3D Printer to use as a static texture,
        #  this will allow users to see their print bed without playing
        #  the Blender Game Renderer
        snapshot_file = self.download_snapshot()
        # Pull in the downloaded picture into current Blender file/scene
        img = self.import_local_image(filename = image_file_name, directory = self.temp_dir)
        # Save image X & Y dimensions to variables for use with scaling preview plane
        image_X_size = img.size[0]
        image_Y_size = img.size[1]
        # Bail with an exception if image dimensions could not be read.
        if image_X_size is None:
            raise Exception('Could not read image X size')
        if image_Y_size is None:
            raise Exception('Could not read image Y size')
        # Add & scale a Plane object, then add the picture from OctoPrint
        #  server as a texture
        preview_plane = self.add_view_plane(image_name = image_file_name, object_name = image_plane_name,
            material_name = bge_material_name, texture_name = bge_texture_name,
            x_dimension = image_X_size, y_dimension = image_Y_size, xy_scale = self.preview_xy_scale)
        # Write a customized Blender Game Engine script for updating the
        #  texture of the Plane with a video source, in this case the
        #  address of the OctoPrint server.
        webcam_script = self.write_bge_script_webcam(controller_script_name = bge_controller_script_name,
            default_image = image_file_name, video_path = self.stream_url)
        # Link together objects, scripts, and Blender Game Engine blocks
        #  such that the user need only use the default keyboard short-cut
        #  'P' within a 3D window to play a live stream from the server.
        self.setup_bge_logic_webcam(object_name = image_plane_name, sensor_name = bge_sensor_name,
            controller_name = bge_controller_name, controller_script_name = bge_controller_script_name)
        # Either update still image or start streaming operations.
        if action == 'snapshot':
            self.modify_viewport_3dview(animate = False)
        elif action == 'stream':
            # Add exit button in upper left corner of preview plane
            # exit_button_location = (-webcam_obj.dimensions[0]/2, webcam_obj.dimensions[1]/2, webcam_obj.dimensions[2]+1)
            exit_button_location = (-preview_plane.dimensions[0]/2, preview_plane.dimensions[1]/2, preview_plane.dimensions[2]+1)
            self.add_text_button(text_name='Exit_Button', text_body='[ESC]', location = exit_button_location)
            # Note we are assuming that naming of background plane will not change from previous function call
            self.setup_bge_logic_button(object_name='Exit_Button_Plane', actuator_type='GAME', actuator_mode='QUIT')
            self.modify_viewport_3dview(animate = True)


#-------------------------------------------------------------------------
#   Custom classes above, Blender buttons bellow
#-------------------------------------------------------------------------


class start_ape_local_button ( Operator ):
    """Start APE in the background"""
    bl_idname = 'object.start_ape_local_button'
    bl_label = 'Start APE Locally'

    def execute ( self, context ):
        return {'FINISHED'}

class start_ape_octoprint_button ( Operator ):
    """Start APE in the background"""
    bl_idname = 'object.start_ape_octoprint_button'
    bl_label = 'Start APE Through OcotoPrint'

    def execute ( self, context ):
        return {'FINISHED'}

class curl_test_button(Operator):
    """Test a curl command from within Blender
    using subprocess.getoutput"""
    bl_idname = 'object.curl_test_button'
    bl_label = 'Curl test command'

    def execute(self, context):
        Scene = context.scene

        if Scene.curl_test_ops is None:
            raise Exception('Please provide curl a list of arguments')
        SP = SubProcess(context)
        curl_getoutput_output = curl_getoutput(ops = Scene.curl_test_ops)

        info = ('# Finished sending the following to curl: {0}'.format(Scene.curl_test_ops))
        self.report({'INFO'}, info)

        info = ('# Output of curl: {0}'.format(curl_getoutput_output))
        self.report({'INFO'}, info)

        return {'FINISHED'}


class local_slice_button(Operator):
    """Export STL to Slic3r, generate GCODE and if configured upload to print server"""
    bl_idname = 'object.local_slice_button'
    bl_label = 'Slice Locally'

    def execute(self, context):
        if not context.selected_objects:
            raise Exception('Please select some objects first.')

        op = Selected_objects(context)
        op_output = op.local_slicer(context)
        op_output.calling_operator = 'local_slice_button(Operator)'
        formated_output = Formatted_output.return_output(op_output)
        for info in formated_output:
            self.report({'INFO'}, info)
        info = ('# ' + op_output.calling_operator + 'finished')
        self.report({'INFO'}, info)
        return {'FINISHED'}


class octoprint_download_file_list_button(Operator):
    """Download a list of files from OctoPrint server"""
    bl_idname = 'object.octoprint_download_file_list'
    bl_label = 'OctoPrint Download File List'

    def execute(self, context):
        Scene = context.scene
        OP = OctoPrint(context)
        downloaded_json = OP.download_json_file_listing(target_search_dir = None)
        parsed_json = OctoPrint.return_file_listing_dict_json(json_file_path = downloaded_json)
        file_list_as_object = OP.return_file_list_as_object(dict_obj = parsed_json)
        if not Scene.octoprint_target_search_dir:
            OctoPrint.print_space_statistics(json_dict = parsed_json)
        OctoPrint.print_folders(folders = file_list_as_object.octoprint_folders)
        OctoPrint.print_machinecode_files(machinecode_files = file_list_as_object.octoprint_machinecode_files)
        OctoPrint.print_model_files(model_files = file_list_as_object.octoprint_model_files)
        info = ('Finished printing OctoPrint target or root folder output to terminal')
        self.report({'INFO'}, info)
        if file_list_as_object.octoprint_folders:
            print('### Printing sub directory Information ###')
            folder_count = 0
            for folder in file_list_as_object.octoprint_folders:
                folder_count += 1
                sub_dir_file_list_as_object = OP.return_file_list_as_object(dict_obj = folder, root_dir = False)
                # print(sub_dir_file_list_as_object.octoprint_folders)
                OctoPrint.print_folders(folders = sub_dir_file_list_as_object.octoprint_folders)
                OctoPrint.print_machinecode_files(machinecode_files = sub_dir_file_list_as_object.octoprint_machinecode_files)
                OctoPrint.print_model_files(model_files = sub_dir_file_list_as_object.octoprint_model_files)
            print('# Sub Directory count', folder_count)
        return {'FINISHED'}


class octoprint_mkdir_button(Operator):
    """Make a directory path on OctoPrint server"""
    bl_idname = 'object.octoprint_mkdir_button'
    bl_label = 'OctoPrint mkdir'

    def execute(self, context):
        Scene = context.scene
        OP = OctoPrint(context)
        OP.mkdir(path = Scene.octoprint_new_dir)

        info = ('Finished making new directory: {0} on host: {1}'.format(Scene.octoprint_new_dir, Scene.octoprint_host))
        self.report({'INFO'}, info)
        return {'FINISHED'}


class octoprint_upload_stl_button(Operator):
    """Upload selected as STL to on OctoPrint server"""
    bl_idname = 'object.octoprint_upload_stl_button'
    bl_label = 'OctoPrint Upload STL'

    def execute(self, context):
        if not context.selected_objects:
            raise Exception('Please select some objects first.')

        Scene = context.scene
        SO = Selected_objects(context)
        OP = OctoPrint(context)
        so_output = SO.export_as_stl(context)
        stls = so_output.blender_export_stl_output
        if isinstance(stls, list):
            for stl in stls:
                op_output = OP.upload_file(stl_path = stl)
        elif stl_file:
            op_output = OP.upload_file(stl_path = stls)

        info = ('Finished uploading selected objects to OctoPrint server')
        self.report({'INFO'}, info)
        return {'FINISHED'}


class preview_webcam_button(Operator):
    """Preform some magic so users can see snapshot of their printer build plate without leaving Blender"""
    bl_idname = 'object.preview_webcam_button'
    bl_label = 'Preview Build Plate'

    def execute(self, context):
        WC = Webcam(context)
        WC.init_preview(action='snapshot')

        info = ('Finished')
        self.report({'INFO'}, info)
        return {'FINISHED'}


class slic3r_repair_button(Operator):
    """Export as STL then import to Slic3r running with --repair and import repaired objects back into Blender"""
    bl_idname = 'object.slic3r_repair_button'
    bl_label = 'Slic3r Repair Selected'
    bl_options = {'REGISTER', 'UNDO'}

    # execute() is called by blender when running the operator
    def execute(self, context):
        if not context.selected_objects:
            raise Exception('Please select some objects first.')
        op = Selected_objects(context)
        op_output = op.repair_through_slic3r(context)
        op_output.calling_operator = 'slic3r_repair_button(Operator)'
        formated_output = Formatted_output.return_output(op_output)
        for info in formated_output:
            self.report({'INFO'}, info)
        info = ('# ' + op_output.calling_operator + 'finished')
        self.report({'INFO'}, info)
        return {'FINISHED'}


class stream_webcam_button(Operator):
    """Preform some more magic so users can see stream of their printer build plate without leaving Blender"""
    bl_idname = 'object.stream_webcam_button'
    bl_label = 'Preview Build Plate'

    def execute(self, context):
        WC = Webcam(context)
        WC.init_preview(action='stream')

        info = ('Finished')
        self.report({'INFO'}, info)
        return {'FINISHED'}


#-------------------------------------------------------------------------
#   Blender buttons above, bellow Blender properties
#-------------------------------------------------------------------------


class curaengine_settings(PropertyGroup):
    Scene = bpy.types.Scene
    if curaengine_exec_dir:
        Scene.curaengine_exec_dir = StringProperty(
            name='CuraEngine path',
            default=curaengine_exec_dir,
            description='CuraEngine executable directory path',
            subtype='DIR_PATH'
        )
    else:
        Scene.curaengine_exec_dir = StringProperty(
            name='CuraEngine path',
            default='',
            description='CuraEngine executable directory path',
            subtype='DIR_PATH'
        )
    if curaengine_exec_name:
        Scene.curaengine_exec_name = StringProperty(
            name='CuraEngine Executable Name',
            default=curaengine_exec_name,
            description='CuraEngine executable name',
        )
    else:
        Scene.curaengine_exec_name = StringProperty(
            name='CuraEngine path',
            default='',
            description='CuraEngine executable name',
        )

    Scene.curaengine_conf_path = StringProperty(
        name='CuraEngine Config',
        default='',
        description='CuraEngine config file path',
        subtype='FILE_PATH'
    )
    Scene.curaengine_extra_args = StringProperty(
        name='CuraEngine Extra Arguments',
        default='',
        description='This is to allow users of older versions of CuraEngine to define slicing settings via command line arguments',
    )
    Scene.export_stl_treat_selected_as = EnumProperty(
        name='Export as:',
        items=(('Individual', 'Individual', ''),
               ('Batch', 'Batch', ''),
               ('Merge', 'Merge', '')),
        default='Individual',
        description='Individual exports selected objects individually, Merge currently only works with local slicing operations for auto-arranging, Batch will export all selected as a single file for all operations. Default: Individual',
    )
    Scene.curaengine_preview_gcode = BoolProperty(
        name='Preview locally sliced GCode',
        description='Opens GCode file(s) within Blender Text Editor when local slicers have finished converting selected object into GCode files. Default: False',
        default=False
    )
    Scene.curaengine_gcode_directory = StringProperty(
        name='Local GCode directory',
        default=bpy.app.tempdir,
        description='Local slicer GCode output directory, default: {0}'.format(bpy.app.tempdir),
        subtype='DIR_PATH'
    )


class curl_settings(PropertyGroup):
    Scene = bpy.types.Scene
    if curl_exec_dir:
        Scene.curl_exec_dir = StringProperty(
            name='Curl path',
            default=curl_exec_dir,
            description='Curl executable directory path',
            subtype='DIR_PATH'
        )
    else:
        Scene.curl_exec_dir = StringProperty(
            name='Curl path',
            default='',
            description='Curl executable directory path',
            subtype='DIR_PATH'
        )
    if curl_exec_name:
        Scene.curl_exec_name = StringProperty(
            name='Curl path',
            default=curl_exec_name,
            description='Curl executable name',
        )
    else:
        Scene.curl_exec_dir = StringProperty(
            name='Curl path',
            default='',
            description='Curl executable name',
        )
    Scene.curl_test_ops = StringProperty(
        name='Curl test arguments',
        default='',
        description='Send Python formatted list of curl arguments from within Blender, for quick testing',
    )


class export_stl_settings(PropertyGroup):
    Scene = bpy.types.Scene
    Scene.export_stl_axis_forward = EnumProperty(
        name='Export STL Axis - Forward',
        description='Which axis should be the relative front of the selected models, default: Y',
        items=(('X', 'X', ''),
               ('Y', 'Y', ''),
               ('Z', 'Z', ''),
               ('-X', '-X', ''),
               ('-Y', '-Y', ''),
               ('-Z', '-Z', '')),
        default='Y',
    )
    Scene.export_stl_axis_up = EnumProperty(
        name='Export STL Axis - Up',
        description='Which axis should be the relative up of the selected models, default: Z',
        items=(('X', 'X', ''),
               ('Y', 'Y', ''),
               ('Z', 'Z', ''),
               ('-X', '-X', ''),
               ('-Y', '-Y', ''),
               ('-Z', '-Z', '')),
        default='Z',
    )
    Scene.export_stl_ascii = BoolProperty(
        name='Export ASCII',
        description='Exports as ASCII text file, default: False',
        default=False
    )
    Scene.export_stl_global_scale = FloatProperty(
        name='Export STL Global Scale',
        description='Scale multiplier to apply to objects being exported, default: 1',
        soft_min=-10,
        soft_max=10,
        precision=5,
        default=1
    )
    Scene.export_stl_use_scene_unit = BoolProperty(
        name='Export STL Use Scene Unit',
        description='Use scene units when exporting objects, default: False',
        default=False
    )
    Scene.export_stl_check_existing = BoolProperty(
        name='Check for Existing STL Files',
        description='Enabled or disables checking for preexisting exported STL files, default: True',
        default=True
    )
    Scene.clean_temp_stl_files = BoolProperty(
        name='Clean-up Temp. STL Files',
        description='Removes temporary STL files after importing or uploading to another application or server, default: True',
        default=True
    )
    Scene.export_stl_treat_selected_as = EnumProperty(
        name='Export individual',
        items=(('Individual', 'Individual', ''),
               ('Batch', 'Batch', ''),
               ('Merge', 'Merge', '')),
        default='Individual',
        description='Individual exports selected objects individually, Merge currently only works with local slicing operations for auto-arranging, Batch will export all selected as a single file for all operations. Default: Individual',
    )
    Scene.export_stl_directory = StringProperty(
        name='Temporary STL file path',
        default=bpy.app.tempdir,
        description='Directory used for temporary STL files generated by this addon, default: {0}'.format(bpy.app.tempdir),
        subtype='DIR_PATH'
    )


class import_obj_settings(PropertyGroup):
    Scene = bpy.types.Scene
    Scene.import_obj_axis_forward = EnumProperty(
        name='Import OBJ Axis - Forward',
        description='Which axis should be the relative front of the imported OBJ files form Slic3r repair, default: Y',
        items=(('X', 'X', ''),
               ('Y', 'Y', ''),
               ('Z', 'Z', ''),
               ('-X', '-X', ''),
               ('-Y', '-Y', ''),
               ('-Z', '-Z', '')),
        default='Y',
    )
    Scene.import_obj_axis_up = EnumProperty(
        name='Import OBJ Axis - Up',
        description='Which axis should be the relative up of the imported OBJ files form Slic3r repair, default: Z',
        items=(('X', 'X', ''),
               ('Y', 'Y', ''),
               ('Z', 'Z', ''),
               ('-X', '-X', ''),
               ('-Y', '-Y', ''),
               ('-Z', '-Z', '')),
        default='Z',
    )
    Scene.import_obj_use_edges = BoolProperty(
        name='Import OBJ Use Edges',
        description='Use edges when importing OBJ files from Slic3r repair operations, default: True',
        default=True
    )
    Scene.import_obj_use_smooth_groups = BoolProperty(
        name='Import OBJ Use Smooth Groups',
        description='Use smooth groups when importing OBJ files from Slic3r repair operations, default: True',
        default=True
    )
    Scene.import_obj_use_split_objects = BoolProperty(
        name='Import OBJ Use Split Objects',
        description='Use split groups when importing OBJ files from Slic3r repair operations, default: True',
        default=True
    )
    Scene.import_obj_use_split_groups = BoolProperty(
        name='Import OBJ Use Split Groups',
        description='Use split groups when importing OBJ files from Slic3r repair operations, default: True',
        default=True
    )
    Scene.import_obj_use_groups_as_vgroups = BoolProperty(
        name='Import OBJ Use Groups As VGroups',
        description='Use groups as vgroups when importing OBJ files from Slic3r repair operations, default: False',
        default=False
    )
    Scene.import_obj_use_image_search = BoolProperty(
        name='Import OBJ Use Image Search',
        description='Use image search when importing OBJ files from Slic3r repair operations, default: True',
        default=True
    )
    Scene.import_obj_split_mode = EnumProperty(
        name='Import OBJ Split Mode',
        description='Activate split mode when importing OBJ files from Slic3r repair operations, default: On',
        items=(('ON', 'On', ''),
               ('OFF', 'Off', '')),
        default='ON',
    )
    Scene.import_obj_global_clamp_size = FloatProperty(
        name='Import OBJ Global Clamp Size',
        description='Global clamp size to use when importing OBJ files from Slic3r repair operations, default: 0',
        soft_min=-10,
        soft_max=10,
        precision=5,
        default=0
    )
    Scene.clean_temp_obj_files = BoolProperty(
        name='Clean-up Temp. OBJ Files',
        description='Removes temporary OBJ files after importing into current Blender scene has finished, default: True',
        default=True
    )
    Scene.import_obj_directory = StringProperty(
        name='Temporary OBJ file path',
        default=bpy.app.tempdir,
        description='Directory used for temporary OBJ files generated by calling Slic3r with "--repair" option, default: {0}'.format(bpy.app.tempdir),
        subtype='DIR_PATH'
    )


class misc_settings(PropertyGroup):
    Scene = bpy.types.Scene
    Scene.preferred_local_slicer = EnumProperty(
        name='Preferred Local Slicer',
        items=(('Slic3r', 'Slic3r', ''),
               ('CuraEngine', 'CuraEngine', '')),
        default='Slic3r',
        description='Local slicer to use for translating exported STL files from Blender into GCode files. Default: Slic3r',
    )
    Scene.preferred_print_server = EnumProperty(
        name='Preferred Print Server',
        items=(('OctoPrint', 'OctoPrint', ''),
               ('Repetier', 'Repetier', '')),
        default='OctoPrint',
        description='3D Printer server to connect to. Default: OctoPrint',
    )
    Scene.log_level = EnumProperty(
        name='Log Level',
        description='Logging & terminal output level, default: Scrubbed',
        items=(('SCRUBBED', 'Scrubbed', ''),
               ('QUITE', 'Quite', ''),
               ('VERBOSE', 'Verbose', ''),),
        default='SCRUBBED',
    )
    Scene.open_browser_after_upload = BoolProperty(
        name='Open Browser after Upload',
        description='Opens a web browser (or new tab) to the uploaded GCode directory if enabled, default: False',
        default=False
    )
    Scene.button_text_color: bpy.props.FloatVectorProperty(
        name='Button Text Color Picker',
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        default=(0.1, 0.75, 0.75, 1.0),
        description='Color text of buttons that get generated by this addon for streaming printer interactions',
    )
    Scene.button_background_color: bpy.props.FloatVectorProperty(
        name='Button Background Color Picker',
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        default=(0.0, 0.0, 0.0, 1.0),
        description='Color background plane of buttons that get generated by this addon for streaming printer interactions',
    )


class octoprint_settings(PropertyGroup):
    Scene = bpy.types.Scene
    Scene.octoprint_auto_upload_from_slicers = BoolProperty(
        name='Upload GCode from Slicers',
        description='Uploads selected objects to OctoPrint server automatically after slicing with a local slicer if enabled, default: False',
        default=False
    )
    Scene.octoprint_host = StringProperty(
        name='OctoPrint host or URL',
        default='http://localhost',
        description='URL or hostname of OctoPrint server, default: http://localhost',
    )
    Scene.octoprint_port = StringProperty(
        name='OctoPrint listening port',
        default='5000',
        description='Listening port of OctoPrint server, default: 5000',
    )
    Scene.octoprint_user = StringProperty(
        name='OctoPrint user name',
        default='',
        description='Authorized user name for connecting through reverse proxy to OctoPrint server',
    )
    Scene.octoprint_pass = StringProperty(
        name='OctoPrint pass-phrase',
        default='',
        description='Authorized pass-phrase for connecting through reverse proxy to OctoPrint server',
        subtype='PASSWORD',
    )
    Scene.octoprint_save_gcode_dir = StringProperty(
        name='OctoPrint GCode directory',
        default='',
        description='Directory to save GCode file uploads to OctoPrint server',
    )
    Scene.octoprint_save_stl_dir = StringProperty(
        name='OctoPrint STL directory',
        default='',
        description='Directory to save STL file uploads to OctoPrint server. Note if slicing server side, this directory is also where OctoPrint will save sliced GCode files',
    )
    Scene.octoprint_api_path = EnumProperty(
        name='OctoPrint upload directory path',
        items=(('/api/files/local', 'local', ''),
               ('/api/files/sdcard', 'sdcard', '')),
        default='/api/files/local',
        description='Mount point to send POST data to OctoPrint server, default: /api/files/local',
    )
    Scene.octoprint_x_api_key = StringProperty(
        name='OctoPrint X-API key',
        default='',
        description='Your client X-API key for interacting with OctoPrint server',
        subtype='PASSWORD',
    )
    Scene.octoprint_new_dir = StringProperty(
        name='OctoPrint new directory',
        default='',
        description='New directory to make on OctoPrint server, just in case someone wanted it in the future, not really necessary at this point though',
    )
    Scene.octoprint_slice_uploaded_stl = BoolProperty(
        name='Slice uploaded STL files with OctoPrint server',
        description='Uploaded STL files will be set to slice into GCode files by OctoPrint server, this is an asynchronous process according to the documentation, default: False',
        default=False
    )
    Scene.octoprint_slice_slicer = StringProperty(
        name='OctoPrint Slicer',
        default='cura',
        description='Slicer to use when slicing uploaded STL files to OctoPrint server, default: cura',
    )
    Scene.octoprint_slice_printerProfile = StringProperty(
        name='OctoPrint Slicer Printer Profile',
        default='',
        description='Printer profile to use, if not set the default printer profile will be used. Hint, this is likely your printer model name',
    )
    Scene.octoprint_slice_Profile = StringProperty(
        name='OctoPrint Slicer Profile',
        default='',
        description='Name of the slicing profile to use, if not set the default slicing profile of the slicer will be used',
    )
    Scene.octoprint_slice_Profile_ops = StringProperty(
        name='OctoPrint Slicer Profile Customizations',
        default='',
        description='Any slicing profile customization to append or overwrite from selected profile, if not set the selected or default slicing profile of the slicer will be used',
    )
    Scene.octoprint_slice_position_x = IntProperty(
        name='OctoPrint Slice Position X',
        description='Position along the X axis that objects should be centered to for slicing into GCode, default: 0',
        default=0
    )
    Scene.octoprint_slice_position_y = IntProperty(
        name='OctoPrint Slice Position Y',
        description='Position along the Y axis that objects should be centered to for slicing into GCode, default: 0',
        default=0
    )
    Scene.octoprint_snapshot_dir = StringProperty(
        name='Temporary .jpg file path',
        default=bpy.app.tempdir,
        description='Directory used for temporary JPG files generated by this addon, default: {0}'.format(bpy.app.tempdir),
        subtype='DIR_PATH'
    )
    Scene.octoprint_temp_dir = StringProperty(
        name='Temporary Directory for OctoPrint',
        default=bpy.app.tempdir,
        description='Directory used for temporary JPG & JSON files generated by this addon, default: {0}'.format(bpy.app.tempdir),
        subtype='DIR_PATH'
    )
    Scene.octoprint_snapshot_name = StringProperty(
        name='Snapshot Name',
        default='OctoPrint_Preview',
        description='Name to use for Snapshot & Video related things that have to be setup within Blender: OctoPrint_Preview',
    )
    Scene.octoprint_camera_port = StringProperty(
        name='Webcam Port',
        default='8080',
        description='Webcam port, set if different than OctoPrint server API port, default: 8080',
    )
    Scene.octoprint_preview_xy_scale = IntProperty(
        name='OctoPrint Preview XY Scale',
        description='Scale divider to apply to preview image plane object based off image pixel size, default: 10',
        default=10,
        min=1,
    )
    Scene.octoprint_snapshot_action = StringProperty(
        name='Snapshot Action',
        default='?action=snapshot',
        description='The URL path to request a snapshot from the server, default: ?action=snapshot',
    )
    Scene.octoprint_stream_action = StringProperty(
        name='Stream Action',
        default='?action=stream',
        description='The URL path to request stream from the server, default: ?action=stream',
    )
    Scene.octoprint_preview_placement = EnumProperty(
        name='Preview Placement',
        description='Where the preview plane will be moved to in relation to global origin, default: Center',
        items=(('CENTER', 'Center', ''),
               ('NORTH', 'North', ''),
               ('EAST', 'East', ''),
               ('SOUTH', 'South', ''),
               ('WEST', 'West', '')),
        default='CENTER',
    )
    Scene.octoprint_preview_layer = IntProperty(
        name='Preview Layer',
        description='What layer within the 3D View will have the preview plane added to, default: 0',
        default=0,
        min=0,
        max=19,
    )
    Scene.octoprint_target_screen = StringProperty(
        name='Target Screen',
        default='Default',
        description='What named screen will have the 3D View ports modified for build plate preview operations, default: Default, hint: bpy.context.screen.name',
    )
    Scene.octoprint_target_3dview = IntProperty(
        name='Target 3D View',
        description='What 3D View will have rendering settings modified, default: 0',
        default=0,
        min=0,
        max=9,
    )
    Scene.octoprint_target_search_dir = StringProperty(
        name='OctoPrint Target Search Dir',
        default='',
        description='Search directory of OctoPrint server by downloading JSON and parsing it, useful for testing future features',
    )


class repetier_settings(PropertyGroup):
    Scene = bpy.types.Scene
    Scene.repetier_auto_upload_from_slicers = BoolProperty(
        name='Upload GCode from Slicers',
        description='Uploads selected objects to Repetier server automatically after slicing into GCode files locally has finished if enabled, default: False',
        default=False
    )
    Scene.repetier_host = StringProperty(
        name='Repetier host or URL',
        default='http://localhost',
        description='URL or hostname of Repetier server, default: http://localhost',
    )
    Scene.repetier_port = StringProperty(
        name='Repetier listening port',
        default='3344',
        description='Listening port of Repetier server, default: 3344',
    )
    Scene.repetier_user = StringProperty(
        name='Repetier user name',
        default='',
        description='Authorized user name for connecting through reverse proxy to Repetier server',
    )
    Scene.repetier_pass = StringProperty(
        name='Repetier pass-phrase',
        default='',
        description='Authorized pass-phrase for connecting through reverse proxy to Repetier server',
        subtype='PASSWORD',
    )
    Scene.repetier_save_gcode_dir = StringProperty(
        name='Repetier GCode directory',
        default='',
        description='Directory to save GCode file uploads to Repetier server. Hint, this is likely your printer model name',
    )
    Scene.repetier_save_stl_dir = StringProperty(
        name='Repetier STL directory',
        default='',
        description='Directory to save STL file uploads to Repetier server',
    )
    Scene.repetier_api_path = StringProperty(
        name='Repetier upload directory path',
        default='/printer/model',
        description='Mount point to send POST data to Repetier server, default: /printer/model',
    )
    Scene.repetier_x_api_key = StringProperty(
        name='Repetier X-API key',
        default='',
        description='Your client X-API key for interacting with Repetier server',
        subtype='PASSWORD',
    )
    Scene.repetier_snapshot_dir = StringProperty(
        name='Temporary .jpg file path',
        default=bpy.app.tempdir,
        description='Directory used for temporary JPG files generated by this addon, default: {0}'.format(bpy.app.tempdir),
        subtype='DIR_PATH'
    )
    Scene.repetier_temp_dir = StringProperty(
        name='Temporary Directory for Repetier',
        default=bpy.app.tempdir,
        description='Directory used for temporary files generated by this addon, default: {0}'.format(bpy.app.tempdir),
        subtype='DIR_PATH'
    )
    Scene.repetier_snapshot_name = StringProperty(
        name='Snapshot Name',
        default='Repetier_Preview',
        description='Name to use for Snapshot & Video related things that have to be setup within Blender: Repetier_Preview',
    )
    Scene.repetier_camera_port = StringProperty(
        name='Webcam Port',
        default='8080',
        description='Webcam port, set if different than Repetier server API port, default: 8080',
    )
    Scene.repetier_preview_xy_scale = IntProperty(
        name='Repetier Preview XY Scale',
        description='Scale divider to apply to preview image plane object based off image pixel size, default: 10',
        default=10,
        min=1,
    )
    Scene.repetier_snapshot_action = StringProperty(
        name='Snapshot Action',
        default='?action=snapshot',
        description='The URL path to request a snapshot from the server, default: ?action=snapshot',
    )
    Scene.repetier_stream_action = StringProperty(
        name='Stream Action',
        default='?action=stream',
        description='The URL path to request stream from the server, default: ?action=stream',
    )
    Scene.repetier_preview_placement = EnumProperty(
        name='Preview Placement',
        description='Where the preview plane will be moved to in relation to global origin, default: Center',
        items=(('CENTER', 'Center', ''),
               ('NORTH', 'North', ''),
               ('EAST', 'East', ''),
               ('SOUTH', 'South', ''),
               ('WEST', 'West', '')),
        default='CENTER',
    )
    # TO-DO - write a function that takes only (self, context) as args, returns nothing
    #  And updates preexisting object placement if the above or bellow settings change
    #  by using: update=function_name(self, context)
    #  within above and bellow property blocks.
    Scene.repetier_preview_layer = IntProperty(
        name='Preview Layer',
        description='What layer within the 3D View will have the preview plane added to, default: 0',
        default=0,
        min=0,
        max=19,
    )
    Scene.repetier_target_screen = StringProperty(
        name='Target Screen',
        default='Default',
        description='What screen name will have the 3D View ports modified for build plate preview operations, default: Default, hint: bpy.context.screen.name',
    )
    Scene.repetier_target_3dview = IntProperty(
        name='Target 3D View',
        description='What 3D View will have rendering settings modified, default: 0',
        default=0,
        min=0,
        max=9,
    )


class slic3r_settings(PropertyGroup):
    Scene = bpy.types.Scene
    if slic3r_exec_dir:
        Scene.slic3r_exec_dir = StringProperty(
            name='Slic3r path',
            default=slic3r_exec_dir,
            description='Slic3r executable directory path',
            subtype='DIR_PATH'
        )
    else:
        Scene.slic3r_exec_dir = StringProperty(
            name='Slic3r path',
            default='',
            description='Slic3r executable directory path',
            subtype='DIR_PATH'
        )

    if slic3r_exec_name:
        Scene.slic3r_exec_name = StringProperty(
            name='Slic3r executable name',
            default=slic3r_exec_name,
            description='Slicer executable name, just in-case addon authors got it wrong, default: {0}'.format(slic3r_exec_name),
        )
    else:
        Scene.slic3r_exec_name = StringProperty(
            name='Slic3r executable name',
            default='',
            description='Slicer executable name, just in-case addon authors got it wrong, default: Unset',
        )

    Scene.slic3r_conf_path = StringProperty(
        name='Slic3r Config',
        default='',
        description='Slic3r config file path. Hint, this should be a file with an ".ini" extension',
        subtype='FILE_PATH'
    )
    Scene.slic3r_post_script = StringProperty(
        name='Slic3r Post Processing Script',
        default='',
        description='File path to GCode post processing script',
        subtype='FILE_PATH'
    )
    Scene.slic3r_extra_args = StringProperty(
        name='Slic3r Extra Arguments',
        default='',
        description='These are applied to the command after any config file is loaded to enable easy & quick edits to an already working config',
    )
    Scene.slic3r_repaired_parent_name = StringProperty(
        name='Repaired parent name',
        default='Slic3r-Fixed-Meshes',
        description='Imported OBJ files will be parented to this named empty, default: Slic3r-Fixed-Meshes',
    )
    Scene.export_stl_treat_selected_as = EnumProperty(
        name='Export as:',
        items=(('Individual', 'Individual', ''),
               ('Batch', 'Batch', ''),
               ('Merge', 'Merge', '')),
        default='Individual',
        description='Individual exports selected objects individually, Merge currently only works with local slicing operations for auto-arranging, Batch will export all selected as a single file for all operations. Default: Individual',
    )
    Scene.slic3r_preview_gcode = BoolProperty(
        name='Preview locally sliced GCode',
        description='Opens GCode file(s) within Blender Text Editor when local slicers have finished converting selected object into GCode files. Default: False',
        default=False
    )
    Scene.slic3r_gcode_directory = StringProperty(
        name='Local GCode directory',
        default=bpy.app.tempdir,
        description='Local slicer GCode output directory, default: {0}'.format(bpy.app.tempdir),
        subtype='DIR_PATH'
    )


#-------------------------------------------------------------------------
#    Panel configurations
#-------------------------------------------------------------------------


class debug_panel(Panel):
    bl_space_type = 'VIEW_3D'                              # What view this panel will be visible to users
    bl_region_type = 'UI'                               # The region the panel will be used in
    bl_context = 'objectmode'                              # The context that this panel belongs to
    bl_category = '3D-Printing'                               # What tab this add-on will be under
    bl_label = 'Debugging Actions'
    bl_idname = 'object.debug_panel'

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        col = layout.column(align=True)

        layout.label(text='Test Curl from Blender')
        layout.prop(scene, 'curl_test_ops', text='Curl argument string')
        layout.operator('object.curl_test_button', text='Test Curl')

        if 'OctoPrint' in scene.preferred_print_server:
            layout.label(text='Test future features')
            layout.prop(scene, 'octoprint_target_search_dir', text='OctoPrint search Dir')
            layout.operator('object.octoprint_download_file_list', text='Parse OctoPrint File list')


class export_stl_config_panel(Panel):
    bl_space_type = 'VIEW_3D'                              # What view this panel will be visible to users
    bl_region_type = 'UI'                               # The region the panel will be used in
    bl_context = 'objectmode'                              # The context that this panel belongs to
    bl_category = '3D-Printing'                               # What tab this add-on will be under
    bl_label = 'Export STL Settings'
    bl_idname = 'object.export_stl_config_panel'

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        col = layout.column(align=True)

        layout.prop(scene, 'clean_temp_stl_files', text='Remove Temporary STL Files')
        layout.prop(scene, 'export_stl_treat_selected_as', text='Export selected as')
        layout.prop(scene, 'export_stl_directory', text='STL Temp Directory')
        layout.prop(scene, 'export_stl_global_scale', text='Global Scale')
        layout.prop(scene, 'export_stl_axis_forward', text='Forward Axis')
        layout.prop(scene, 'export_stl_axis_up', text='Up Axis')
        layout.prop(scene, 'export_stl_ascii', text='ASCII Format')
        layout.prop(scene, 'export_stl_use_scene_unit', text='Use Scene Unit')
        layout.prop(scene, 'export_stl_check_existing', text='Check Existing Prior to Export')


class import_obj_config_panel(Panel):
    bl_space_type = 'VIEW_3D'                              # What view this panel will be visible to users
    bl_region_type = 'UI'                               # The region the panel will be used in
    bl_context = 'objectmode'                              # The context that this panel belongs to
    bl_category = '3D-Printing'                               # What tab this add-on will be under
    bl_label = 'Import OBJ Settings'
    bl_idname = 'object.import_obj_config_panel'

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        col = layout.column(align=True)

        layout.prop(scene, 'clean_temp_obj_files', text='Remove Temporary OBJ Files')
        layout.prop(scene, 'import_obj_directory', text='OBJ Temp Directory')
        layout.prop(scene, 'import_obj_global_clamp_size', text='OBJ Global Clamp Size')
        layout.prop(scene, 'import_obj_axis_forward', text='OBJ Axis Forward')
        layout.prop(scene, 'import_obj_axis_up', text='OBJ Axis Up')
        layout.prop(scene, 'import_obj_use_edges', text='OBJ Use Edges')
        layout.prop(scene, 'import_obj_use_smooth_groups', text='OBJ Use Smooth Groups')
        layout.prop(scene, 'import_obj_use_split_objects', text='OBJ Use Split Objects')
        layout.prop(scene, 'import_obj_use_split_groups', text='OBJ Use Split Groups')
        layout.prop(scene, 'import_obj_use_groups_as_vgroups', text='OBJ Use Groups as VGroups')
        layout.prop(scene, 'import_obj_use_image_search', text='OBJ Use Image Search')
        layout.prop(scene, 'import_obj_split_mode', text='OBJ Split Mode')


class slicer_config_panel(Panel):
    bl_space_type = 'VIEW_3D'                              # What view this panel will be visible to users
    bl_region_type = 'UI'                               # The region the panel will be used in
    bl_context = 'objectmode'                              # The context that this panel belongs to
    bl_category = '3D-Printing'                               # What tab this add-on will be under
    bl_label = 'Local Slicer Settings'
    bl_idname = 'object.slicer_config_panel'

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        col = layout.column(align=True)

        layout.prop(scene, 'preferred_local_slicer', text='Preferred Local Slicer')
        if 'Slic3r' in scene.preferred_local_slicer:
            layout.prop(scene, 'slic3r_exec_dir', text='Directory of Executable')
            layout.prop(scene, 'slic3r_exec_name', text='Name of Executable')
            layout.prop(scene, 'slic3r_conf_path', text='Slic3r Configuration File')
            layout.prop(scene, 'slic3r_post_script', text='Post Processing Script')
            layout.prop(scene, 'slic3r_extra_args', text='Extra Arguments')
            layout.prop(scene, 'slic3r_gcode_directory', text='GCode Save Directory')
        elif 'CuraEngine' in scene.preferred_local_slicer:
            layout.prop(scene, 'curaengine_exec_dir', text='Directory of Executable')
            layout.prop(scene, 'curaengine_exec_name', text='Name of Executable')
            layout.prop(scene, 'curaengine_conf_path', text='Configuration File')
            layout.prop(scene, 'curaengine_extra_args', text='Extra Arguments')
            layout.prop(scene, 'curaengine_gcode_directory', text='GCode Save Directory')


class print_server_connection_panel(Panel):
    bl_space_type = 'VIEW_3D'                              # What view this panel will be visible to users
    bl_region_type = 'UI'                               # The region the panel will be used in
    bl_context = 'objectmode'                              # The context that this panel belongs to
    bl_category = '3D-Printing'                               # What tab this add-on will be under
    bl_label = 'Server Connection Settings'
    bl_idname = 'object.print_server_connection_panel'

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        col = layout.column(align=True)

        layout.prop(scene, 'preferred_print_server', text='Prefered Printer Server')
        if 'OctoPrint' in scene.preferred_print_server:
            layout.prop(scene, 'octoprint_auto_upload_from_slicers', text='Upload GCode from Slicers')
            layout.prop(scene, 'open_browser_after_upload', text='Open Browser After Upload')
            layout.prop(scene, 'octoprint_host', text='Host URL')
            layout.prop(scene, 'octoprint_port', text='Host Port')
            layout.prop(scene, 'octoprint_user', text='User Name')
            layout.prop(scene, 'octoprint_pass', text='Passphrase')
            layout.prop(scene, 'octoprint_api_path', text='POST Directory')
            layout.prop(scene, 'octoprint_save_gcode_dir', text='GCode Directory')
            layout.prop(scene, 'octoprint_save_stl_dir', text='STL Directory')
            layout.prop(scene, 'octoprint_x_api_key', text='X-API Key')
        elif 'Repetier' in scene.preferred_print_server:
            layout.prop(scene, 'repetier_auto_upload_from_slicers', text='Upload GCode from Slicers')
            layout.prop(scene, 'open_browser_after_upload', text='Open Browser After Upload')
            layout.prop(scene, 'repetier_host', text='Host URL')
            layout.prop(scene, 'repetier_port', text='Host Port')
            layout.prop(scene, 'repetier_user', text='User Name')
            layout.prop(scene, 'repetier_pass', text='Passphrase')
            layout.prop(scene, 'repetier_api_path', text='POST Directory')
            layout.prop(scene, 'repetier_save_gcode_dir', text='GCode Directory')
            # layout.prop(scene, 'repetier_save_stl_dir', text='STL Directory')
            layout.prop(scene, 'repetier_x_api_key', text='X-API Key')

        layout.label(text="Curl executable configurations")
        layout.prop(scene, 'curl_exec_dir', text='Directory of Executable')
        layout.prop(scene, 'curl_exec_name', text='Name of Executable')


class print_server_buttons_panel(Panel):
    bl_space_type = 'VIEW_3D'                              # What view this panel will be visible to users
    bl_region_type = 'UI'                               # The region the panel will be used in
    bl_context = 'objectmode'                              # The context that this panel belongs to
    bl_category = '3D-Printing'                               # What tab this add-on will be under
    bl_label = 'Print Server Actions'
    bl_idname = 'object.print_server_buttons_panel'

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        col = layout.column(align=True)

        layout.prop(scene, 'preferred_print_server', text='Preferred Printer Server')
        layout.operator('object.preview_webcam_button', text='Preview Build Plate')
        layout.operator('object.stream_webcam_button', text='Stream Build Plate')
        if 'OctoPrint' in scene.preferred_print_server:
            layout.prop(scene, 'octoprint_api_path', text='POST Directory')
            layout.prop(scene, 'octoprint_new_dir', text='New Directory Path')
            layout.operator('object.octoprint_mkdir_button', text='Make New Directory')
            layout.prop(scene, 'octoprint_save_stl_dir', text='STL Directory')
            layout.operator('object.octoprint_upload_stl_button', text='Upload Selected as STL')
            layout.prop(scene, 'octoprint_slice_uploaded_stl', text='Slice Uploaded STL(s)')
        # if 'Repetier' in scene.preferred_print_server:
        #     print('# To-Do')
            # TO-DO - see about making functions & classes to handle the following features
            # layout.prop(scene, 'repetier_new_dir', text='New Directory Path')
            # layout.operator('object.repetier_mkdir_button', text='Make New Directory')
            # layout.operator('object.repetier_upload_stl_button', text='Upload Selected as STL')
            # layout.prop(scene, 'repetier_slice_uploaded_stl', text='Slice Uploaded STL(s)')
            # layout.prop(scene, 'repetier_save_stl_dir', text='STL Directory')


class print_server_slicer_panel(Panel):
    bl_space_type = 'VIEW_3D'                              # What view this panel will be visible to users
    bl_region_type = 'UI'                               # The region the panel will be used in
    bl_context = 'objectmode'                              # The context that this panel belongs to
    bl_category = '3D-Printing'                               # What tab this add-on will be under
    bl_label = 'Server Slicer Settings'
    bl_idname = 'object.print_server_slicer_panel'

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        col = layout.column(align=True)

        layout.prop(scene, 'preferred_print_server', text='Preferred Printer Server')
        if 'OctoPrint' in scene.preferred_print_server:
            layout.prop(scene, 'octoprint_slice_uploaded_stl', text='Slice Uploaded STL(s)')
            layout.prop(scene, 'octoprint_slice_slicer', text='Slicer Name')
            layout.prop(scene, 'octoprint_slice_printerProfile', text='Printer Profile')
            layout.prop(scene, 'octoprint_slice_Profile', text='Slicer Profile')
            layout.prop(scene, 'octoprint_slice_Profile_ops', text='Slicer Profile Customizations')
            layout.prop(scene, 'octoprint_slice_position_x', text='Slicer X Position')
            layout.prop(scene, 'octoprint_slice_position_y', text='Slicer Y Position')
        if 'Repetier' in scene.preferred_print_server:
            layout.label(text="One day maybe")


class quick_slicer_tools_buttons_panel(Panel):
    bl_space_type = 'VIEW_3D'                              # What view this panel will be visible to users
    bl_region_type = 'UI'                               # The region the panel will be used in
    bl_context = 'objectmode'                              # The context that this panel belongs to
    bl_category = '3D-Printing'                               # What tab this add-on will be under
    bl_label = 'Quick Slicer Tools'                        # Display name in the interface
    bl_idname = 'object.quick_slicer_tools_buttons_panel'  # Unique ID for buttons & menu items

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        col = layout.column(align=True)

        layout.prop(scene, 'export_stl_treat_selected_as', text='Export as Individual Files')
        layout.operator('object.slic3r_repair_button', text='Slic3r Repair Selected')
        layout.prop(scene, 'slic3r_repaired_parent_name', text='Repaired Parent Name')
        layout.prop(scene, 'preferred_local_slicer', text='Preferred Local Slicer')
        layout.operator('object.local_slice_button', text='Slice Selected Locally')
        layout.prop(scene, 'slic3r_gcode_directory', text='GCode Save Directory')
        if 'Slic3r' in scene.preferred_local_slicer:
            layout.prop(scene, 'slic3r_preview_gcode', text='Preview GCode')
        elif 'CuraEngine' in scene.preferred_local_slicer:
            layout.prop(scene, 'curaengine_preview_gcode', text='Preview GCode')
        layout.prop(scene, 'preferred_print_server', text='Preferred Printer Server')
        if 'OctoPrint' in scene.preferred_print_server:
            layout.prop(scene, 'octoprint_auto_upload_from_slicers', text='OctoPrint Upload GCode')
        if 'Repetier' in scene.preferred_print_server:
            layout.prop(scene, 'repetier_auto_upload_from_slicers', text='Repetier Upload GCode')
        layout.prop(scene, 'open_browser_after_upload', text='Open Browser After GCode Upload')
        layout.prop(scene, 'log_level', text='Logging Level')


class webcam_config_panel(Panel):
    bl_space_type = 'VIEW_3D'                              # What view this panel will be visible to users
    bl_region_type = 'UI'                               # The region the panel will be used in
    bl_context = 'objectmode'                              # The context that this panel belongs to
    bl_category = '3D-Printing'                               # What tab this add-on will be under
    bl_label = 'Server Webcam Settings'
    bl_idname = 'object.webcam_config_panel'

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        col = layout.column(align=True)

        layout.prop(scene, 'preferred_print_server', text='Prefered Printer Server')
        if 'OctoPrint' in scene.preferred_print_server:
            layout.prop(scene, 'octoprint_target_screen', text='Target Screen Name')
            layout.prop(scene, 'octoprint_target_3dview', text='Target 3D View')
            layout.prop(scene, 'octoprint_snapshot_dir', text='JPG Directory')
            layout.prop(scene, 'octoprint_snapshot_name', text='Snapshot Name')
            layout.prop(scene, 'octoprint_camera_port', text='Webcam Port')
            layout.prop(scene, 'octoprint_snapshot_action', text='Snapshot Action')
            layout.prop(scene, 'octoprint_stream_action', text='Stream Action')
            layout.prop(scene, 'octoprint_preview_placement', text='Preview Placement')
            layout.prop(scene, 'octoprint_preview_layer', text='Layer to Place Preview')
            layout.prop(scene, 'octoprint_preview_xy_scale', text='XY Scale')
        elif 'Repetier' in scene.preferred_print_server:
            layout.prop(scene, 'repetier_target_screen', text='Target Screen Name')
            layout.prop(scene, 'repetier_target_3dview', text='Target 3D View')
            layout.prop(scene, 'repetier_snapshot_dir', text='JPG Directory')
            layout.prop(scene, 'repetier_snapshot_name', text='Snapshot Name')
            layout.prop(scene, 'repetier_camera_port', text='Webcam Port')
            layout.prop(scene, 'repetier_snapshot_action', text='Snapshot Action')
            layout.prop(scene, 'repetier_stream_action', text='Stream Action')
            layout.prop(scene, 'repetier_preview_placement', text='Preview Placement')
            layout.prop(scene, 'repetier_preview_layer', text='Layer to Place Preview')
            layout.prop(scene, 'repetier_preview_xy_scale', text='XY Scale')
        layout.prop(scene, 'button_background_color', text='Button Background Color')
        layout.prop(scene, 'button_text_color', text='Button Text Color')


#-------------------------------------------------------------------------
#    Register & un-register configs, note order determines initial layout of panels
#-------------------------------------------------------------------------
classes = (
    import_obj_settings,
    export_stl_settings,
    slic3r_settings,
    curaengine_settings,
    curl_settings,
    octoprint_settings,
    repetier_settings,
    misc_settings,

    slic3r_repair_button,
    local_slice_button,
    octoprint_mkdir_button,
    octoprint_upload_stl_button,
    curl_test_button,
    preview_webcam_button,
    stream_webcam_button,
    octoprint_download_file_list_button,

    quick_slicer_tools_buttons_panel,
    print_server_buttons_panel,
    export_stl_config_panel,
    import_obj_config_panel,
    slicer_config_panel,
    print_server_connection_panel,
    print_server_slicer_panel,
    webcam_config_panel,
    debug_panel)


#-------------------------------------------------------------------------
#   Register classes and other UI stuff
#-------------------------------------------------------------------------
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.utils.register_manual_map(print_shortcuts_manual_map)


#-------------------------------------------------------------------------
#   Un-register classes and other UI stuff
#-------------------------------------------------------------------------
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.utils.unregister_manual_map(print_shortcuts_manual_map)


#-------------------------------------------------------------------------
#    Registration configuration
#-------------------------------------------------------------------------
def menu_func(self, context):
    layout = self.layout
    layout.operator(quick_slicer_tools_buttons_panel.bl_idname)
    layout.operator(export_stl_config_panel.bl_idname)
    layout.operator(import_obj_config_panel.bl_idname)
    layout.operator(slicer_config_panel.bl_idname)
    layout.operator(debug_panel.bl_idname)
    layout.operator(print_server_buttons_panel.bl_idname)
    layout.operator(print_server_connection_config_panel.bl_idname)
    layout.operator(print_server_slicer_config_panel.bl_idname)
    layout.operator(preview_webcam_config_panel.bl_idname)


#-------------------------------------------------------------------------
#    This allows you to right click on a button and link to the manual
#-------------------------------------------------------------------------
def print_shortcuts_manual_map():
    url_manual_prefix = 'https://docs.blender.org/manual/en/dev/'
    url_manual_mapping = (
        ('bpy.object.print_shortcuts', 'to-be-decided'),
    )
    return url_manual_prefix, url_manual_mapping


# Uncomment the following two lines to allow add-on to run from text editor
#  without having to install via user preferences
if __name__ == '__main__':
    __name__ = this_addons_name
    register()
