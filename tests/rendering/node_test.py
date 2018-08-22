from unittest import TestCase, main
from unittest.mock import Mock
from pyviews.testing import case
from pyviews.core.xml import XmlNode, XmlAttr
from pyviews.core.observable import InheritedDict, Observable
from pyviews.core.compilation import CompilationError
from pyviews.core.node import Node, InstanceNode
from pyviews.core.ioc import Services
from pyviews.rendering.node import Code
from pyviews.rendering.node import get_init_args, create_node, create_inst, convert_to_node, RenderingError

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
    def test_methods_definitions(self, content, globals_dict, expected):
        parent_globals = self._get_parent_globals(globals_dict)
        code = self._get_code_node(parent_globals, content)

        code.render_children()

        msg = 'defined functions should be added to parent globals'
        for key, value in expected.items():
            self.assertEqual(value, parent_globals[key](), msg)

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
    def test_variables_definitions(self, content, globals_dict, expected):
        parent_globals = self._get_parent_globals(globals_dict)
        code = self._get_code_node(parent_globals, content)

        code.render_children()

        msg = 'defined functions should be added to parent globals'
        for key, value in expected.items():
            self.assertEqual(value, parent_globals[key], msg)

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
    def test_raises_error(self, content, globals_dict):
        parent_globals = self._get_parent_globals(globals_dict)
        code = self._get_code_node(parent_globals, content)

        msg = 'render_children should raise CompilationError for invalid code'
        with self.assertRaises(CompilationError, msg=msg):
            code.render_children()

    def _get_code_node(self, parent_globals, content):
        parent_node = Mock()
        parent_node.globals = parent_globals
        code = Code(parent_node, None)
        code.text = content
        return code

    def _get_parent_globals(self, globals_dict):
        parent_globals = InheritedDict()
        for key, value in globals_dict.items():
            parent_globals[key] = value
        return parent_globals

class Inst:
    def __init__(self, xml_node, parent_node):
        self.xml_node = xml_node
        self.parent_node = parent_node

class InstReversed:
    def __init__(self, parent_node, xml_node):
        self.xml_node = xml_node
        self.parent_node = parent_node

class SecondInst:
    def __init__(self, xml_node, parent_node=None):
        self.xml_node = xml_node
        self.parent_node = parent_node

class ThirdInst:
    def __init__(self, xml_node=None, parent_node=None):
        self.xml_node = xml_node
        self.parent_node = parent_node

class InitTests(TestCase):
    @case(Inst, {'xml_node': 1, 'parent_node': 'node'}, [1, 'node'], {})
    @case(InstReversed, {'xml_node': 1, 'parent_node': 'node'}, ['node', 1], {})
    @case(SecondInst, {'xml_node': 1, 'parent_node': 'node'}, [1], {'parent_node': 'node'})
    @case(ThirdInst, {'xml_node': 1, 'parent_node': 'node'}, [], {'xml_node': 1, 'parent_node': 'node'})
    def test_get_init_args(self, inst_type, init_args, args, kwargs):
        actual_args, actual_kwargs = get_init_args(inst_type, **init_args)

        msg = 'get_init_args should return args for inst_type constructor'
        self.assertEqual(args, actual_args, msg)
        self.assertEqual(kwargs, actual_kwargs, msg)

    @case(Inst, {})
    @case(Inst, {'xml_node': 1})
    @case(Inst, {'parent_node': 'node'})
    @case(InstReversed, {'xml_node': 1})
    @case(InstReversed, {'parent_node': 'node'})
    @case(SecondInst, {})
    @case(SecondInst, {'parent_node': 'node'})
    def test_get_init_args_raises(self, inst_type, init_args):
        msg = 'get_init_args should raise RenderingError if there are no required arguments'
        with self.assertRaises(RenderingError, msg=msg):
            get_init_args(inst_type, **init_args)

    @case(Inst, {'xml_node': 1, 'parent_node': 'node'})
    @case(InstReversed, {'xml_node': 1, 'parent_node': 'node'})
    @case(SecondInst, {'xml_node': 1, 'parent_node': 'node'})
    @case(ThirdInst, {'xml_node': 1, 'parent_node': 'node'})
    def test_create_inst_should_return_instance_of_passed_type(self, inst_type, init_args):
        inst = create_inst(inst_type, **init_args)

        msg = 'create_inst should return instance of passed type'
        self.assertIsInstance(inst, inst_type, msg)

    @case({})
    @case({'one': 1})
    def test_convert_to_node_should_create_node(self, globals_dict):
        inst = Mock()
        xml_node = Mock()

        node = convert_to_node(inst, xml_node, node_globals=InheritedDict(globals_dict))

        msg = 'convert_to_node should create InstanceNode'
        self.assertIsInstance(node, InstanceNode, msg)

        msg = 'convert_to_node should pass globals'
        self.assertDictContainsSubset(globals_dict, node.globals.to_dictionary(), msg)

    @case('pyviews.core.node', 'Node', Node, {})
    @case('pyviews.rendering.node', 'Code', Code, {'parent_node': Node(None)})
    def test_create_node_creates_node(self, namespace, tag, node_type, init_args):
        xml_node = XmlNode(namespace, tag)

        node = create_node(xml_node, **init_args)

        msg = 'create_node should create instance using namespace as module and tag name as class name'
        self.assertIsInstance(node, node_type, msg)

    @case('pyviews.core.node', 'UnknownNode')
    @case('pyviews.core.unknownModule', 'Node')
    def test_create_node_raises(self, namespace, tag):
        xml_node = XmlNode(namespace, tag)

        msg = 'create_node should raise in case module or class cannot be imported'
        with self.assertRaises(RenderingError, msg=msg):
            create_node(xml_node)

    @case('pyviews.core.observable', 'Observable', Observable)
    @case('pyviews.core.ioc', 'Services', Services)
    def test_create_node_creates_instance_node(self, namespace, tag, inst_type):
        xml_node = XmlNode(namespace, tag)

        node = create_node(xml_node)

        msg = 'create_node should create instance node'
        self.assertIsInstance(node, InstanceNode, msg)

        msg = 'create_node should create instance using namespace as module and tag name as class name'
        self.assertIsInstance(node.instance, inst_type, msg)

if __name__ == '__main__':
    main()
