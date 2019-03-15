# pylint: disable=missing-docstring

from unittest import TestCase
from unittest.mock import Mock
from pyviews.testing import case
from pyviews.core.observable import InheritedDict
from pyviews.core.compilation import CompilationError
from pyviews.core.xml import XmlNode
from pyviews.core.node import Node
from pyviews.code import Code, run_code

class CodeTests(TestCase):
    @case(
        '''
        def none():
            return None

        def one():
            return 1

        def str_value():
            return 'str_value'

        def global_key():
            return key
        ''',
        {'key': 'key'},
        {'none': None, 'one': 1, 'str_value': 'str_value', 'global_key': 'key'})
    def test_run_code_adds_methods_definitions(self, content, globals_dict, expected):
        parent_node = Node(Mock())
        code = self._get_code_node(content)

        run_code(code, parent_node=parent_node, node_globals=InheritedDict(globals_dict))

        msg = 'defined functions should be added to parent globals'
        for key, value in expected.items():
            self.assertEqual(value, parent_node.node_globals[key](), msg)

    @case(
        '''
        one = 1
        str_value = 'str_value'
        global_key = key
        ''',
        {'key': 'key'},
        {'one': 1, 'str_value': 'str_value', 'global_key': 'key'})
    @case(
        '''
            one = 1
            str_value = 'str_value'
            global_key = key
        ''',
        {'key': 'key'},
        {'one': 1, 'str_value': 'str_value', 'global_key': 'key'})
    def test_run_code_adds_variables_definitions(self, content, globals_dict, expected):
        parent_node = Node(Mock())
        code = self._get_code_node(content)

        run_code(code, parent_node=parent_node, node_globals=InheritedDict(globals_dict))

        msg = 'variables should be added to parent globals'
        for key, value in expected.items():
            self.assertEqual(value, parent_node.node_globals[key], msg)

    @case('''a = key.prop''', {'key': None})
    @case('''a = key.prop''', {})
    @case('''2/0''', {})
    @case(
        '''
        def some_func():
        pass
        ''', {})
    @case(
        '''
        def some_func()
            pass
        ''', {})
    def test_run_code_raises_error(self, content, globals_dict):
        parent_node = Node(Mock())
        code = self._get_code_node(content)

        msg = 'render_children should raise CompilationError for invalid code'
        with self.assertRaises(CompilationError, msg=msg):
            run_code(code, parent_node=parent_node, node_globals=InheritedDict(globals_dict))

    @staticmethod
    def _get_code_node(content):
        xml_node = XmlNode('namespace', 'name')
        xml_node.text = content
        return Code(xml_node)
