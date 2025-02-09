# <pep8 compliant>
# Written by Stephan Vedder and Michael Schnabel

import bpy
import os
import sys
from mathutils import Quaternion, Matrix, Vector
from bpy_extras.image_utils import load_image


def make_transform_matrix(loc, rot):
    mat_loc = Matrix.Translation(loc)
    mat_rot = Quaternion(rot).to_matrix().to_4x4()
    return mat_loc @ mat_rot


def get_objects(type, object_list=None):  # MESH, ARMATURE
    if object_list is None:
        object_list = bpy.context.scene.objects
    return [obj for obj in object_list if obj.type == type]


def switch_to_pose(rig, pose):
    if rig is not None:
        rig.data.pose_position = pose
        bpy.context.view_layer.update()


def insensitive_path(path):
    # find the io_stream on unix
    directory = os.path.dirname(path)
    name = os.path.basename(path)

    for io_stream_name in os.listdir(directory):
        if io_stream_name.lower() == name.lower():
            path = os.path.join(directory, io_stream_name)
    return path


def get_collection(hlod=None, index=''):
    if hlod is not None:
        name = hlod.model_name() + index
        if name in bpy.data.collections:
            return bpy.data.collections[name]
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
        return coll
    return bpy.context.scene.collection


def link_object_to_active_scene(obj, coll):
    coll.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)


def rig_object(obj, hierarchy, rig, sub_object):
    obj.parent = rig
    obj.parent_type = 'ARMATURE'
    if sub_object.bone_index <= 0:
        return

    pivot = hierarchy.pivots[sub_object.bone_index]

    obj.parent_bone = pivot.name
    obj.parent_type = 'BONE'


def create_uvlayer(context, mesh, b_mesh, tris, mat_pass):
    tx_coords = None
    if mat_pass.tx_coords:
        tx_coords = mat_pass.tx_coords
    else:
        if mat_pass.tx_stages:
            if len(mat_pass.tx_stages[0].tx_coords) == 0:
                context.warning('texture stage did not have texture coordinates!')
                return
            tx_coords = mat_pass.tx_stages[0].tx_coords[0]
            if len(mat_pass.tx_stages[0].tx_coords) > 1:
                context.warning('only one set of texture coordinates per texture stage supported')
        if len(mat_pass.tx_stages) > 1:
            context.warning('only one texture stage per material pass supported')

    if tx_coords is None:
        return

    uv_layer = mesh.uv_layers.new(do_init=False)
    for i, face in enumerate(b_mesh.faces):
        for loop in face.loops:
            idx = tris[i][loop.index % 3]
            uv_layer.data[loop.index].uv = tx_coords[idx].xy


extensions = ['.dds', '.tga', '.jpg', '.jpeg', '.png', '.bmp']


def find_texture(context, file, name=None):
    file = file.rsplit('.', 1)[0]
    if name is None:
        name = file
    else:
        name = name.rsplit('.', 1)[0]

    for extension in extensions:
        combined = name + extension
        if combined in bpy.data.images:
            return bpy.data.images[combined]

    path = insensitive_path(os.path.dirname(context.filepath))
    filepath = path + os.path.sep + file

    img = None
    for extension in extensions:
        img = load_image(filepath + extension)
        if img is not None:
            context.info('loaded texture: ' + filepath + extension)
            img.name = name + extension
            break

    if img is None:
        context.warning(
            f'texture not found: {filepath} {extensions}. Make sure it is right next to the file you are importing!')
        img = bpy.data.images.new(name, width=2048, height=2048)
        img.generated_type = 'COLOR_GRID'
        img.source = 'GENERATED'
        img.name = name + extensions[0]

    img.alpha_mode = 'STRAIGHT'
    return img


def get_aa_box(vertices):
    minX = sys.float_info.max
    maxX = sys.float_info.min

    minY = sys.float_info.max
    maxY = sys.float_info.min

    minZ = sys.float_info.max
    maxZ = sys.float_info.min

    for vertex in vertices:
        minX = min(vertex.co.x, minX)
        maxX = max(vertex.co.x, maxX)

        minY = min(vertex.co.y, minY)
        maxY = max(vertex.co.y, maxY)

        minZ = min(vertex.co.z, minZ)
        maxZ = max(vertex.co.z, maxZ)

    return Vector((maxX - minX, maxY - minY, maxZ - minZ))
