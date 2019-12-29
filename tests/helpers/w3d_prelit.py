# <pep8 compliant>
# Written by Stephan Vedder and Michael Schnabel

import unittest
from mathutils import Vector
from io_mesh_w3d.structs.w3d_prelit import *
from tests.helpers.w3d_material_info import *
from tests.helpers.w3d_material_pass import *
from tests.helpers.w3d_vertex_material import *
from tests.helpers.w3d_texture import *
from tests.helpers.w3d_shader import*


def get_prelit(type=W3D_CHUNK_PRELIT_UNLIT, count=1):
    result = PrelitBase(
        type=type,
        mat_info=None,
        material_passes=[],
        vert_materials=[],
        textures=[],
        shaders=[])

    result.mat_info = MaterialInfo(
        pass_count=count,
        vert_matl_count=count,
        shader_count=count,
        texture_count=count)

    for _ in range(count):
        result.material_passes.append(get_material_pass())
        result.vert_materials.append(get_vertex_material())
        result.textures.append(get_texture())
        result.shaders.append(get_shader())
    return result


def get_prelit_minimal(type=W3D_CHUNK_PRELIT_UNLIT):
    return PrelitBase(
        type=type,
        mat_info=get_material_info(),
        material_passes=[],
        vert_materials=[],
        textures=[],
        shaders=[])


def compare_prelits(self, expected, actual):
    self.assertEqual(expected.type, actual.type)
    compare_material_infos(self, expected.mat_info, actual.mat_info)

    self.assertEqual(len(expected.material_passes), len(actual.material_passes))
    for i, mat_pass in enumerate(expected.material_passes):
        compare_material_passes(self, mat_pass, actual.material_passes[i])

    self.assertEqual(len(expected.vert_materials), len(actual.vert_materials))
    for i, vert_mat in enumerate(expected.vert_materials):
        compare_vertex_materials(self, vert_mat, actual.vert_materials[i])

    self.assertEqual(len(expected.textures), len(actual.textures))
    for i, tex in enumerate(expected.textures):
        compare_textures(self, tex, actual.textures[i])

    self.assertEqual(len(expected.shaders), len(actual.shaders))
    for i, shader in enumerate(expected.shaders):
        compare_shaders(self, shader, actual.shaders[i])
