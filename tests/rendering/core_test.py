from unittest import TestCase, main
from unittest.mock import Mock, call
from tests.mock import some_modifier
from pyviews.testing import case
from pyviews.core.xml import XmlNode, XmlAttr
from pyviews.core.node import Node, InstanceNode
from pyviews.core.observable import InheritedDict, Observable
from pyviews.core.ioc import Scope, register_single, scope, Services
from pyviews.rendering import core
from pyviews.rendering.dependencies import register_defaults
from pyviews.rendering.node import Code

class NodeRenderingTests(TestCase):
    def setUp(self):
        xml_node = XmlNode('pyviews.core.node', 'Node')
        self.parent_node = Node(xml_node)

        self.xml_node = XmlNode('pyviews.core.node', 'Node')
        with Scope('NodeRenderingTests'):
            register_defaults()

    # @scope('NodeRenderingTests')
    # def test_render(self):
    #     self.parent_node.globals['some_key'] = 'some value'

    #     node = core.render(self.xml_node, RenderArgs(self.xml_node, self.parent_node))

    #     msg = 'parse should init node with right passed xml_node'
    #     self.assertIsInstance(node, Node, msg=msg)

    #     msg = 'parse should init node with passed parent'
    #     self.assertEqual(node.globals['some_key'], 'some value', msg=msg)

class SomeObject:
    def __init__(self):
        pass

class ParseObjectNodeTests(TestCase):
    def setUp(self):
        self.xml_node = XmlNode('tests.rendering.core_test', 'SomeObject')
        with Scope('ParseObjectNodeTests'):
            register_defaults()

    # @scope('ParseObjectNodeTests')
    # def test_parse_raises(self):
    #     msg = 'parse should raise error if method "convert_to_node" is not registered'
    #     with self.assertRaises(core.RenderingError, msg=msg):
    #         core.render(self.xml_node, core.RenderArgs(self.xml_node))

def set_attr():
    pass

class GetModifierTests(TestCase):
    def setUp(self):
        with Scope('modifier_tests'):
            register_single('set_attr', set_attr)

    @scope('modifier_tests')
    @case(None, '', set_attr)
    @case(None, 'attr_name', set_attr)
    @case('tests.rendering.core_test.some_modifier', '', some_modifier)
    @case('tests.rendering.core_test.some_modifier', 'attr_name', some_modifier)
    def test_get_modifier(self, namespace, name, expected):
        xml_attr = XmlAttr(name, '', namespace)
        actual = core.get_modifier(xml_attr)
        self.assertEqual(actual, expected)

    @scope('modifier_tests')
    @case('', '')
    @case('', 'attr_name')
    @case('tests.rendering.core_test.some_modifier_not', 'attr_name')
    def test_get_modifier_raises(self, namespace, name):
        msg = 'get_modifier should raise ImportError if namespace can''t be imported'
        with self.assertRaises(ImportError, msg=msg):
            xml_attr = XmlAttr(name, '', namespace)
            core.get_modifier(xml_attr)

class RenderStepTests(TestCase):
    @case({})
    @case({'key': 1})
    def test_render_step(self, args):
        step = Mock()
        decorated_step = core.render_step(step)
        node = Mock()

        decorated_step(node, args)

        msg = 'render_step pass node to step'
        self.assertEqual(step.call_args, call(node), msg)

    @case({})
    @case({'key': 1, 'key2': 'value'})
    def test_render_step_with_parameters(self, args):
        step = Mock()
        decorated_step = core.render_step(*args.keys())(step)
        node = Mock()

        decorated_step(node, args)

        msg = 'render_step should pass args to step'
        self.assertEqual(step.call_args, call(node, **args), msg)

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
        actual_args, actual_kwargs = core.get_init_args(inst_type, **init_args)

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
        with self.assertRaises(core.RenderingError, msg=msg):
            core.get_init_args(inst_type, **init_args)

    @case(Inst, {'xml_node': 1, 'parent_node': 'node'})
    @case(InstReversed, {'xml_node': 1, 'parent_node': 'node'})
    @case(SecondInst, {'xml_node': 1, 'parent_node': 'node'})
    @case(ThirdInst, {'xml_node': 1, 'parent_node': 'node'})
    def test_create_inst_should_return_instance_of_passed_type(self, inst_type, init_args):
        inst = core.create_inst(inst_type, **init_args)

        msg = 'create_inst should return instance of passed type'
        self.assertIsInstance(inst, inst_type, msg)

    @case({})
    @case({'one': 1})
    def test_convert_to_node_should_create_node(self, globals_dict):
        inst = Mock()
        xml_node = Mock()

        node = core.convert_to_node(inst, xml_node, node_globals=InheritedDict(globals_dict))

        msg = 'convert_to_node should create InstanceNode'
        self.assertIsInstance(node, InstanceNode, msg)

        msg = 'convert_to_node should pass globals'
        self.assertDictContainsSubset(globals_dict, node.globals.to_dictionary(), msg)

    @case('pyviews.core.node', 'Node', Node, {})
    @case('pyviews.rendering.node', 'Code', Code, {'parent_node': Node(None)})
    def test_create_node_creates_node(self, namespace, tag, node_type, init_args):
        xml_node = XmlNode(namespace, tag)

        node = core.create_node(xml_node, **init_args)

        msg = 'create_node should create instance using namespace as module and tag name as class name'
        self.assertIsInstance(node, node_type, msg)

    @case('pyviews.core.node', 'UnknownNode')
    @case('pyviews.core.unknownModule', 'Node')
    def test_create_node_raises(self, namespace, tag):
        xml_node = XmlNode(namespace, tag)

        msg = 'create_node should raise in case module or class cannot be imported'
        with self.assertRaises(core.RenderingError, msg=msg):
            core.create_node(xml_node)

    @case('pyviews.core.observable', 'Observable', Observable)
    @case('pyviews.core.ioc', 'Services', Services)
    def test_create_node_creates_instance_node(self, namespace, tag, inst_type):
        xml_node = XmlNode(namespace, tag)

        node = core.create_node(xml_node)

        msg = 'create_node should create instance node'
        self.assertIsInstance(node, InstanceNode, msg)

        msg = 'create_node should create instance using namespace as module and tag name as class name'
        self.assertIsInstance(node.instance, inst_type, msg)

if __name__ == '__main__':
    main()
