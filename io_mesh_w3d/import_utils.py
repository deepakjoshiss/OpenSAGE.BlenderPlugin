# <pep8 compliant>
# Written by Stephan Vedder and Michael Schnabel

import bpy

from io_mesh_w3d.common.utils.mesh_import import *
from io_mesh_w3d.common.utils.hierarchy_import import *
from io_mesh_w3d.common.utils.animation_import import *
from io_mesh_w3d.common.utils.box_import import *
from io_mesh_w3d.w3d.utils.dazzle_import import *


def create_data(
        context,
        meshes,
        hlod=None,
        hierarchy=None,
        boxes=[],
        animation=None,
        compressed_animation=None,
        dazzles=[]):
    collection = get_collection(hlod)
    rig = get_or_create_skeleton(hlod, hierarchy, collection)

    if hlod is not None:
        current_coll = collection
        for i, lod_array in enumerate(reversed(hlod.lod_arrays)):
            if i > 0:
                current_coll = get_collection(hlod, '.' + str(i))
                current_coll.hide_viewport = True

            for sub_object in lod_array.sub_objects:
                for mesh in [_ for _ in meshes if _.name() == sub_object.name]:
                    create_mesh(context, mesh, current_coll)

                for box in [_ for _ in boxes if _.name() == sub_object.name]:
                    create_box(box, hlod, hierarchy, rig, current_coll)

                for dazzle in [_ for _ in dazzles if _.name() == sub_object.name]:
                    create_dazzle(context, dazzle, current_coll)

        for lod_array in reversed(hlod.lod_arrays):
            for sub_object in lod_array.sub_objects:
                for mesh in [_ for _ in meshes if _.name() == sub_object.name]:
                    rig_mesh(mesh, hierarchy, rig, sub_object)
                for dazzle in [_ for _ in dazzles if _.name() == sub_object.name]:
                    dazzle_object = bpy.data.objects[dazzle.name()]
                    rig_object(dazzle_object, hierarchy, rig, sub_object)

    else:
        for mesh in meshes:
            create_mesh(context, mesh, collection)

    create_animation(rig, animation, hierarchy)
    create_animation(rig, compressed_animation, hierarchy, compressed=True)
