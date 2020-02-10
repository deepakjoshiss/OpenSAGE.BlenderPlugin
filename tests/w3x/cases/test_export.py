# <pep8 compliant>
# Written by Stephan Vedder and Michael Schnabel

import os.path

from io_mesh_w3d.import_utils import *
from io_mesh_w3d.export_utils import save
from tests.common.helpers.hierarchy import *
from tests.common.helpers.hlod import *
from tests.common.helpers.mesh import *
from tests.utils import *


class TestExportW3X(TestCase):
    def test_unsupported_export_mode(self):
        export_settings = {}
        export_settings['mode'] = 'NON_EXISTING'

        context = IOWrapper(self.outpath() + 'output_skn', 'W3X')

        self.assertEqual({'CANCELLED'}, save(context, export_settings))

    def test_no_hlod_is_written_if_mode_M(self):
        export_settings = {}
        export_settings['mode'] = 'M'
        export_settings['compression'] = 'U'
        export_settings['individual_files'] = False
        export_settings['create_texture_xmls'] = False

        meshes = [get_mesh()]
        create_data(self, meshes)

        extension = '.w3x'
        file_path = self.outpath() + 'output_skn'
        context = IOWrapper(file_path, 'W3X')

        self.assertEqual({'FINISHED'}, save(context, export_settings))

        root = find_root(self, file_path + extension)
        self.assertIsNone(root.find('W3DContainer'))

    def test_no_hierarchy_is_written_if_mode_M(self):
        export_settings = {}
        export_settings['mode'] = 'M'
        export_settings['compression'] = 'U'
        export_settings['individual_files'] = False
        export_settings['create_texture_xmls'] = False

        meshes = [get_mesh()]
        create_data(self, meshes)

        extension = '.w3x'
        file_path = self.outpath() + 'output_skn'
        context = IOWrapper(file_path, 'W3X')

        self.assertEqual({'FINISHED'}, save(context, export_settings))

        root = find_root(self, file_path + extension)
        self.assertIsNone(root.find('W3DHierarchy'))

    def test_hierarchy_is_written_if_mode_HM_and_not_use_existing_skeleton(self):
        export_settings = {}
        export_settings['mode'] = 'HM'
        export_settings['compression'] = 'U'
        export_settings['individual_files'] = False
        export_settings['create_texture_xmls'] = False
        export_settings['use_existing_skeleton'] = False

        hierarchy_name = 'TestHiera_SKL'
        hierarchy = get_hierarchy(hierarchy_name)
        meshes = [
            get_mesh(name='sword', skin=True),
            get_mesh(name='soldier', skin=True),
            get_mesh(name='TRUNK')]
        hlod = get_hlod('TestModelName', hierarchy_name)

        create_data(self, meshes, hlod, hierarchy)

        extension = '.w3x'
        file_path = self.outpath() + 'output_skn'
        context = IOWrapper(file_path, 'W3X')

        self.assertEqual({'FINISHED'}, save(context, export_settings))

        root = find_root(self, file_path + extension)
        self.assertIsNotNone(root.find('W3DHierarchy'))

    def test_no_hierarchy_is_written_if_mode_HM_and_use_existing_skeleton(self):
        export_settings = {}
        export_settings['mode'] = 'HM'
        export_settings['compression'] = 'U'
        export_settings['individual_files'] = False
        export_settings['create_texture_xmls'] = False
        export_settings['use_existing_skeleton'] = True

        hierarchy_name = 'TestHiera_SKL'
        hierarchy = get_hierarchy(hierarchy_name)
        meshes = [
            get_mesh(name='sword', skin=True),
            get_mesh(name='soldier', skin=True),
            get_mesh(name='TRUNK')]
        hlod = get_hlod('TestModelName', hierarchy_name)

        create_data(self, meshes, hlod, hierarchy)

        extension = '.w3x'
        file_path = self.outpath() + 'output_skn'
        context = IOWrapper(file_path, 'W3X')

        self.assertEqual({'FINISHED'}, save(context, export_settings))

        root = find_root(self, file_path + extension)
        self.assertIsNone(root.find('W3DHierarchy'))

    def test_no_texture_xml_files_are_created_if_not_create_texture_xmls(self):
        export_settings = {}
        export_settings['mode'] = 'HM'
        export_settings['individual_files'] = False
        export_settings['create_texture_xmls'] = False
        export_settings['use_existing_skeleton'] = False

        hierarchy_name = 'TestHiera_SKL'
        hierarchy = get_hierarchy(hierarchy_name)
        meshes = [
            get_mesh(name='sword', skin=True),
            get_mesh(name='soldier', skin=True),
            get_mesh(name='TRUNK')]
        hlod = get_hlod('TestModelName', hierarchy_name)

        create_data(self, meshes, hlod, hierarchy)

        extension = '.w3x'
        file_path = self.outpath() + 'output_skn'
        context = IOWrapper(file_path, 'W3X')

        self.assertEqual({'FINISHED'}, save(context, export_settings))

        self.assertTrue(os.path.exists(file_path + extension))
        self.assertFalse(os.path.exists(self.outpath() + 'texture.xml'))

    def test_texture_xml_files_are_created_if_create_texture_xmls(self):
        export_settings = {}
        export_settings['mode'] = 'HM'
        export_settings['individual_files'] = False
        export_settings['create_texture_xmls'] = True
        export_settings['use_existing_skeleton'] = False

        hierarchy_name = 'TestHiera_SKL'
        hierarchy = get_hierarchy(hierarchy_name)
        meshes = [
            get_mesh(name='sword', skin=True),
            get_mesh(name='soldier', skin=True),
            get_mesh(name='TRUNK')]
        hlod = get_hlod('TestModelName', hierarchy_name)

        create_data(self, meshes, hlod, hierarchy)

        extension = '.w3x'
        file_path = self.outpath() + 'output_skn'
        context = IOWrapper(file_path, 'W3X')

        self.assertEqual({'FINISHED'}, save(context, export_settings))

        self.assertTrue(os.path.exists(file_path + extension))
        self.assertTrue(os.path.exists(self.outpath() + 'texture.xml'))
