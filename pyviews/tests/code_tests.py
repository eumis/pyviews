from unittest.mock import Mock

from pytest import mark, raises

from pyviews.code import Code, run_code
from pyviews.core.compilation import CompilationError
from pyviews.core.node import Node
from pyviews.core.observable import InheritedDict
from pyviews.core.xml import XmlNode
from pyviews.rendering.common import RenderingContext


class RunCodeTests:
    """Code.run_code tests"""

    @mark.parametrize('content, globals_dict, expected', [
        (
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
                {'none': None, 'one': 1, 'str_value': 'str_value', 'global_key': 'key'}
        )
    ])
    def test_adds_methods_definitions(self, content, globals_dict, expected):
        """defined functions should be added to parent globals"""
        parent_node = Node(Mock())
        code = self._get_code_node(content)
        context = RenderingContext({'parent_node': parent_node, 'node_globals': InheritedDict(globals_dict)})

        run_code(code, context)

        for key, value in expected.items():
            assert value == parent_node.node_globals[key]()

    @mark.parametrize('content, globals_dict, expected', [
        (
                '''
                one = 1
                str_value = 'str_value'
                global_key = key
                ''',
                {'key': 'key'},
                {'one': 1, 'str_value': 'str_value', 'global_key': 'key'}
        ),
        (
                '''
                    one = 1
                    str_value = 'str_value'
                    global_key = key
                ''',
                {'key': 'key'},
                {'one': 1, 'str_value': 'str_value', 'global_key': 'key'}
        )
    ])
    def test_adds_variables_definitions(self, content, globals_dict, expected):
        """variables should be added to parent globals"""
        parent_node = Node(Mock())
        code = self._get_code_node(content)
        context = RenderingContext({'parent_node': parent_node, 'node_globals': InheritedDict(globals_dict)})

        run_code(code, context)

        for key, value in expected.items():
            assert value == parent_node.node_globals[key]

    @mark.parametrize('content, globals_dict', [
        ('''a = key.prop''', {'key': None}),
        ('''a = key.prop''', {}),
        ('''2/0''', {}),
        (
                '''
                def some_func():
                pass
                ''', {}),
        (
                '''
                def some_func()
                    pass
                ''', {})
    ])
    def test_raises_error(self, content, globals_dict):
        """should raise CompilationError for invalid code"""
        parent_node = Node(Mock())
        code = self._get_code_node(content)
        context = RenderingContext({'parent_node': parent_node, 'node_globals': InheritedDict(globals_dict)})

        with raises(CompilationError):
            run_code(code, context)

    @staticmethod
    def _get_code_node(content):
        xml_node = XmlNode('namespace', 'name')
        xml_node.text = content
        return Code(xml_node)
