# <pep8 compliant>
# Written by Stephan Vedder and Michael Schnabel

import bpy
from bpy.types import Panel
from bpy_extras.io_utils import ImportHelper, ExportHelper
from io_mesh_w3d.utils import ReportHelper
from io_mesh_w3d.export_utils import save_data
from io_mesh_w3d.custom_properties import *
from io_mesh_w3d.geometry_export import *
from io_mesh_w3d.bone_volume_export import *

from io_mesh_w3d.blender_addon_updater import addon_updater_ops

VERSION = (0, 6, 9)

bl_info = {
    'name': 'Import/Export Westwood W3D Format (.w3d/.w3x)',
    'author': 'OpenSage Developers',
    'version': (0, 6, 7),
    "blender": (2, 90, 0),
    'location': 'File > Import/Export > Westwood W3D (.w3d/.w3x)',
    'description': 'Import or Export the Westwood W3D-Format (.w3d/.w3x)',
    'warning': 'Still in Progress',
    'doc_url': 'https://github.com/OpenSAGE/OpenSAGE.BlenderPlugin',
    'tracker_url': 'https://github.com/OpenSAGE/OpenSAGE.BlenderPlugin/issues',
    'support': 'OFFICIAL',
    'category': 'Import-Export'}


def print_version(info):
    version = str(VERSION).replace('(', '').replace(')', '')
    version = version.replace(',', '.').replace(' ', '')
    info(f'plugin version: {version}  unofficial')


class ExportW3D(bpy.types.Operator, ExportHelper, ReportHelper):
    """Export to Westwood 3D file format (.w3d/.w3x)"""
    bl_idname = 'export_mesh.westwood_w3d'
    bl_label = 'Export W3D/W3X'
    bl_options = {'UNDO', 'PRESET'}

    filename_ext = ''

    filter_glob: StringProperty(default='*.w3d;*.w3x', options={'HIDDEN'})

    file_format: bpy.props.EnumProperty(
        name="Format",
        items=(
            ('W3D',
             'Westwood 3D Binary (.w3d)',
             'Exports to W3D format, which was used in earlier SAGE games.'
             'Namely Command and Conquer Generals and the Battle for Middleearth series'),
            ('W3X',
             'Westwood 3D XML (.w3x)',
             'Exports to W3X format, which was used in later SAGE games.'
             'Namely everything starting from Command and Conquer 3')),
        description="Select the export file format",
        default='W3D')

    export_mode: EnumProperty(
        name='Mode',
        items=(
            ('HM',
             'Hierarchical Model',
             'This will export all the meshes of the scene with hierarchy/skeleton data'),
            ('HAM',
             'Hierarchical Animated Model',
             'This will export all the meshes of the scene with hierarchy/skeleton and animation data'),
            ('A',
             'Animation',
             'This will export the animation without any geometry or hierarchy/skeleton data'),
            ('H',
             'Hierarchy',
             'This will export the hierarchy/skeleton without any geometry or animation data'),
            ('M',
             'Mesh',
             'This will export a simple mesh (only the first of the scene if there are multiple), \
                without any hierarchy/skeleton and animation data')),
        description='Select the export mode',
        default='HM')

    use_existing_skeleton: BoolProperty(
        name='Use existing skeleton', description='Use an already existing skeleton (.skn)', default=False)

    animation_compression: EnumProperty(
        name='Compression',
        items=(('U', 'Uncompressed', 'This will not compress the animations'),
               ('TC', 'TimeCoded', 'This will export the animation with keyframes'),
               # ('AD', 'AdaptiveDelta',
               # 'This will use adaptive delta compression to reduce size'),
               ),
        description='The method used for compressing the animation data',
        default='U')

    force_vertex_materials: BoolProperty(
        name='Force Vertex Materials', description='Export all materials as Vertex Materials only', default=False)

    individual_files: BoolProperty(
        name='Individual files',
        description='Creates an individual file for each mesh, boundingbox and the hierarchy',
        default=False)

    create_texture_xmls: BoolProperty(
        name='Create texture xml files', description='Creates an .xml file for each used texture', default=False)

    will_save_settings: BoolProperty(default=False)

    scene_key = 'w3dExportSettings'

    def invoke(self, context, event):
        settings = context.scene.get(self.scene_key)
        self.will_save_settings = False
        if settings:
            try:
                for (k, v) in settings.items():
                    setattr(self, k, v)
                self.will_save_settings = True

            except (AttributeError, TypeError):
                self.error('Loading export settings failed. Removed corrupted settings.')
                del context.scene[self.scene_key]

        return ExportHelper.invoke(self, context, event)

    def save_settings(self, context):
        all_props = self.properties
        export_props = {x: getattr(self, x) for x in dir(
            all_props) if x.startswith('export_') and all_props.get(x) is not None}

        context.scene[self.scene_key] = export_props

    def execute(self, context):
        print_version(self.info)
        if self.will_save_settings:
            self.save_settings(context)

        export_settings = {'mode': self.export_mode,
                           'compression': self.animation_compression,
                           'use_existing_skeleton': self.use_existing_skeleton,
                           'individual_files': self.individual_files,
                           'create_texture_xmls': self.create_texture_xmls}

        return save_data(self, export_settings)

    def draw(self, _context):
        self.draw_general_settings()
        if self.export_mode == 'HM':
            self.draw_use_existing_skeleton()
            if self.file_format == 'W3X':
                self.draw_individual_files()

        if self.file_format == 'W3X' and 'M' in self.export_mode:
            self.draw_create_texture_xmls()

        if self.file_format == 'W3D' and 'M' in self.export_mode:
            self.draw_force_vertex_materials()

        if (self.export_mode == 'A' or self.export_mode == 'HAM') \
                and not self.file_format == 'W3X':
            self.draw_animation_settings()

    def draw_general_settings(self):
        col = self.layout.box().column()
        col.prop(self, 'file_format')
        col = self.layout.box().column()
        col.prop(self, 'export_mode')

    def draw_use_existing_skeleton(self):
        col = self.layout.box().column()
        col.prop(self, 'use_existing_skeleton')

    def draw_animation_settings(self):
        col = self.layout.box().column()
        col.prop(self, 'animation_compression')

    def draw_force_vertex_materials(self):
        col = self.layout.box().column()
        col.prop(self, 'force_vertex_materials')

    def draw_individual_files(self):
        col = self.layout.box().column()
        col.prop(self, 'individual_files')

    def draw_create_texture_xmls(self):
        col = self.layout.box().column()
        col.prop(self, 'create_texture_xmls')


class ImportW3D(bpy.types.Operator, ImportHelper, ReportHelper):
    """Import from Westwood 3D file format (.w3d/.w3x)"""
    bl_idname = 'import_mesh.westwood_w3d'
    bl_label = 'Import W3D/W3X'
    bl_options = {'UNDO'}

    file_format = ''

    filter_glob: StringProperty(default='*.w3d;*.w3x', options={'HIDDEN'})

    def execute(self, context):
        print_version(self.info)
        if self.filepath.lower().endswith('.w3d'):
            from .w3d.import_w3d import load
            file_format = 'W3D'
            load(self)
        else:
            from .w3x.import_w3x import load
            file_format = 'W3X'
            load(self)

        self.info('finished')
        return {'FINISHED'}


def menu_func_export(self, _context):
    self.layout.operator(ExportW3D.bl_idname, text='Westwood W3D (.w3d/.w3x)')


def menu_func_import(self, _context):
    self.layout.operator(ImportW3D.bl_idname, text='Westwood W3D (.w3d/.w3x)')


class MESH_PROPERTIES_PANEL_PT_w3d(Panel):
    bl_label = 'W3D Properties'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'

    def draw(self, context):
        obj = context.active_object
        if (obj.type != 'MESH'):
            return

        layout = self.layout
        col = layout.column()
        mesh = context.active_object.data
        col.prop(mesh, 'object_type')
        col = layout.column()
        if mesh.object_type == 'MESH':
            col.prop(mesh, 'sort_level')
            col = layout.column()
            col.prop(mesh, 'casts_shadow')
            col = layout.column()
            col.prop(mesh, 'two_sided')
            col = layout.column()
            col.prop(mesh, 'userText')
        elif mesh.object_type == 'DAZZLE':
            col = layout.column()
            col.prop(mesh, 'dazzle_type')
        elif mesh.object_type == 'BOX':
            col = layout.column()
            col.prop(mesh, 'box_type')
            col = layout.column()
            col.prop(mesh, 'box_collision_types')
        elif mesh.object_type == 'GEOMETRY':
            col = layout.column()
            col.prop(mesh, 'geometry_type')
            col = layout.column()
            col.prop(mesh, 'contact_points_type')
        elif mesh.object_type == 'BONE_VOLUME':
            col = layout.column()
            col.prop(mesh, 'mass')
            col = layout.column()
            col.prop(mesh, 'spinniness')
            col = layout.column()
            col.prop(mesh, 'contact_tag')


class BONE_PROPERTIES_PANEL_PT_w3d(Panel):
    bl_label = 'W3D Properties'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'bone'

    def draw(self, context):
        layout = self.layout
        if context.active_bone is not None:
            col = layout.column()
            col.prop(context.active_bone, 'visibility')


class MATERIAL_PROPERTIES_PANEL_PT_w3d(Panel):
    bl_label = 'W3D Properties'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'material'

    def draw(self, context):
        layout = self.layout
        mat = context.object.active_material
        col = layout.column()
        col.prop(mat, 'material_type')

        if mat.material_type == 'PRELIT_MATERIAL':
            col = layout.column()
            col.prop(mat, 'prelit_type')

        col = layout.column()
        col.prop(mat, 'surface_type')
        col = layout.column()
        col.prop(mat, 'blend_mode')
        col = layout.column()
        col.prop(mat, 'ambient')

        if mat.material_type == 'VERTEX_MATERIAL' or mat.material_type == 'PRELIT_MATERIAL':
            col = layout.column()
            col.prop(mat, 'specular')
            col = layout.column()
            col.prop(mat, 'attributes')
            col = layout.column()
            col.prop(mat, 'translucency')
            col = layout.column()
            col.prop(mat, 'stage0_mapping')
            col = layout.column()
            col.prop(mat, 'vm_args_0')
            col = layout.column()
            col.prop(mat, 'stage1_mapping')
            col = layout.column()
            col.prop(mat, 'vm_args_1')

            col = layout.column()
            layout.label(text="Shader Properties")
            col = layout.column()
            col.prop(mat.shader, 'depth_compare')
            col = layout.column()
            col.prop(mat.shader, 'depth_mask')
            col = layout.column()
            col.prop(mat.shader, 'color_mask')
            col = layout.column()
            col.prop(mat.shader, 'dest_blend')
            col = layout.column()
            col.prop(mat.shader, 'fog_func')
            col = layout.column()
            col.prop(mat.shader, 'pri_gradient')
            col = layout.column()
            col.prop(mat.shader, 'sec_gradient')
            col = layout.column()
            col.prop(mat.shader, 'src_blend')
            col = layout.column()
            col.prop(mat.shader, 'detail_color_func')
            col = layout.column()
            col.prop(mat.shader, 'detail_alpha_func')
            col = layout.column()
            col.prop(mat.shader, 'shader_preset')
            col = layout.column()
            col.prop(mat.shader, 'alpha_test')
            col = layout.column()
            col.prop(mat.shader, 'post_detail_color_func')
            col = layout.column()
            col.prop(mat.shader, 'post_detail_alpha_func')

        else:
            col = layout.column()
            col.prop(mat, 'technique')
            col.prop(mat, 'alpha_test')
            col = layout.column()
            col.prop(mat, 'bump_uv_scale')
            col = layout.column()
            col.prop(mat, 'edge_fade_out')
            col = layout.column()
            col.prop(mat, 'depth_write')
            col = layout.column()
            col.prop(mat, 'sampler_clamp_uv_no_mip_0')
            col = layout.column()
            col.prop(mat, 'sampler_clamp_uv_no_mip_1')
            col = layout.column()
            col.prop(mat, 'num_textures')
            col = layout.column()
            col.prop(mat, 'texture_1')
            col = layout.column()
            col.prop(mat, 'secondary_texture_blend_mode')
            col = layout.column()
            col.prop(mat, 'tex_coord_mapper_0')
            col = layout.column()
            col.prop(mat, 'tex_coord_mapper_1')
            col = layout.column()
            col.prop(mat, 'tex_coord_transform_0')
            col = layout.column()
            col.prop(mat, 'tex_coord_transform_1')
            col = layout.column()
            col.prop(mat, 'environment_texture')
            col = layout.column()
            col.prop(mat, 'environment_mult')
            col = layout.column()
            col.prop(mat, 'recolor_texture')
            col = layout.column()
            col.prop(mat, 'recolor_mult')
            col = layout.column()
            col.prop(mat, 'use_recolor')
            col = layout.column()
            col.prop(mat, 'house_color_pulse')
            col = layout.column()
            col.prop(mat, 'scrolling_mask_texture')
            col = layout.column()
            col.prop(mat, 'tex_coord_transform_angle')
            col = layout.column()
            col.prop(mat, 'tex_coord_transform_u_0')
            col = layout.column()
            col.prop(mat, 'tex_coord_transform_v_0')
            col = layout.column()
            col.prop(mat, 'tex_coord_transform_u_1')
            col = layout.column()
            col.prop(mat, 'tex_coord_transform_v_1')
            col = layout.column()
            col.prop(mat, 'tex_coord_transform_u_2')
            col = layout.column()
            col.prop(mat, 'tex_coord_transform_v_2')
            col = layout.column()
            col.prop(mat, 'tex_ani_fps_NPR_lastFrame_frameOffset_0')
            col = layout.column()
            col.prop(mat, 'ion_hull_texture')
            col = layout.column()
            col.prop(mat, 'multi_texture_enable')


class TOOLS_PANEL_PT_w3d(bpy.types.Panel):
    bl_label = 'W3D Tools'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        self.layout.operator('scene.export_geometry_data', icon='CUBE', text='Export Geometry Data')
        self.layout.operator('scene.export_bone_volume_data', icon='BONE_DATA', text='Export Bone Volume Data')


class OBJECT_PT_DemoUpdaterPanel(bpy.types.Panel):
    bl_label = 'Updater Demo Panel'
    bl_idname = 'OBJECT_PT_hello'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = 'objectmode'
    bl_category = 'Tools'

    def draw(self, context):
        layout = self.layout

        addon_updater_ops.check_for_update_background()

        layout.label(text='Demo Updater Addon')
        layout.label(text='')

        col = layout.column()
        col.scale_y = 0.7
        col.label(text='If an update is ready,')
        col.label(text='popup triggered by opening')
        col.label(text='this panel, plus a box ui')

        if addon_updater_ops.updater.update_ready:
            layout.label(text='An update for the W3D/W3X plugin is available', icon='INFO')
        layout.label(text='')

        addon_updater_ops.update_notice_box_ui(self, context)


@addon_updater_ops.make_annotations
class DemoPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    auto_check_update = bpy.props.BoolProperty(
        name='Auto-check for Update',
        description='If enabled, auto-check for updates using an interval',
        default=False,
    )
    updater_intrval_months = bpy.props.IntProperty(
        name='Months',
        description='Number of months between checking for updates',
        default=0,
        min=0
    )
    updater_intrval_days = bpy.props.IntProperty(
        name='Days',
        description='Number of days between checking for updates',
        default=7,
        min=0,
        max=31
    )
    updater_intrval_hours = bpy.props.IntProperty(
        name='Hours',
        description='Number of hours between checking for updates',
        default=0,
        min=0,
        max=23
    )
    updater_intrval_minutes = bpy.props.IntProperty(
        name='Minutes',
        description='Number of minutes between checking for updates',
        default=0,
        min=0,
        max=59
    )

    def draw(self, context):
        layout = self.layout

        mainrow = layout.row()
        col = mainrow.column()

        addon_updater_ops.update_settings_ui(self, context)


CLASSES = (
    ExportW3D,
    ImportW3D,
    ShaderProperties,
    MESH_PROPERTIES_PANEL_PT_w3d,
    BONE_PROPERTIES_PANEL_PT_w3d,
    MATERIAL_PROPERTIES_PANEL_PT_w3d,
    ExportGeometryData,
    ExportBoneVolumeData,
    TOOLS_PANEL_PT_w3d,
    DemoPreferences,
    OBJECT_PT_DemoUpdaterPanel
)


def register():
    addon_updater_ops._package = 'io_mesh_w3d'
    addon_updater_ops.updater.addon = 'io_mesh_w3d'
    addon_updater_ops.updater.user = "OpenSAGE"
    addon_updater_ops.updater.repo = "OpenSAGE.BlenderPlugin"
    addon_updater_ops.updater.website = "https://github.com/OpenSAGE/OpenSAGE.BlenderPlugin"
    addon_updater_ops.updater.subfolder_path = "io_mesh_w3d"
    addon_updater_ops.updater.include_branch_list = ['master']
    addon_updater_ops.updater.verbose = False

    addon_updater_ops.register(bl_info)

    for class_ in CLASSES:
        bpy.utils.register_class(class_)

    Material.shader = PointerProperty(type=ShaderProperties)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    addon_updater_ops.unregister()

    for class_ in reversed(CLASSES):
        bpy.utils.unregister_class(class_)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == '__main__':
    register()
