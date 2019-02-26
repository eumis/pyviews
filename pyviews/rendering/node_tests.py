#pylint: disable=missing-docstring, invalid-name

from unittest import TestCase
from unittest.mock import Mock
from pyviews.testing import case
from pyviews.core import XmlNode, Node, InstanceNode
from pyviews.core import InheritedDict, Observable
from pyviews.core.ioc import Services
from pyviews.code import Code
from .common import RenderingError
from .node import get_init_args, convert_to_node
from .node import create_node, create_inst

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

class FourthInst:
    def __init__(self, xml_node, *args, parent_node=None, **kwargs):
        self.xml_node = xml_node
        self.parent_node = parent_node

class InstWithKwargs:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

class get_init_args_tests(TestCase):
    @case(Inst, {'xml_node': 1, 'parent_node': 'node'}, [1, 'node'], {}, True)
    @case(Inst, {'xml_node': 1, 'parent_node': 'node'}, [1, 'node'], {}, False)
    @case(InstReversed, {'xml_node': 1, 'parent_node': 'node'}, ['node', 1], {}, True)
    @case(InstReversed, {'xml_node': 1, 'parent_node': 'node'}, ['node', 1], {}, False)
    @case(SecondInst, {'xml_node': 1, 'parent_node': 'node'}, [1], {'parent_node': 'node'}, True)
    @case(SecondInst, {'xml_node': 1, 'parent_node': 'node'}, [1], {'parent_node': 'node'}, False)
    @case(ThirdInst, {'xml_node': 1, 'parent_node': 'node'}, [], {'xml_node': 1, 'parent_node': 'node'}, True)
    @case(ThirdInst, {'xml_node': 1, 'parent_node': 'node'}, [], {'xml_node': 1, 'parent_node': 'node'}, False)
    @case(FourthInst, {'xml_node': 1, 'parent_node': 'node', 'some_key': 'value'}, [1], {'parent_node': 'node', 'some_key': 'value'}, True)
    @case(FourthInst, {'xml_node': 1, 'parent_node': 'node', 'some_key': 'value'}, [1], {'parent_node': 'node'}, False)
    @case(InstWithKwargs, {'xml_node': 1, 'parent_node': 'node'}, [], {'xml_node': 1, 'parent_node': 'node'}, True)
    @case(InstWithKwargs, {'xml_node': 1, 'parent_node': 'node'}, [], {}, False)
    def test_returns_args_kwargs_for_constructor(self, inst_type, init_args, args, kwargs, add_kwargs):
        actual_args, actual_kwargs = get_init_args(inst_type, init_args, add_kwargs=add_kwargs)

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
    def test_raises_if_init_args_not_contain_key(self, inst_type, init_args):
        msg = 'get_init_args should raise RenderingError if there are no required arguments'
        with self.assertRaises(RenderingError, msg=msg):
            get_init_args(inst_type, init_args)

class create_inst_tests(TestCase):
    @case(Inst, {'xml_node': 1, 'parent_node': 'node'})
    @case(InstReversed, {'xml_node': 1, 'parent_node': 'node'})
    @case(SecondInst, {'xml_node': 1, 'parent_node': 'node'})
    @case(ThirdInst, {'xml_node': 1, 'parent_node': 'node'})
    def test_returns_instance_of_passed_type(self, inst_type, init_args):
        inst = create_inst(inst_type, **init_args)

        msg = 'create_inst should return instance of passed type'
        self.assertIsInstance(inst, inst_type, msg)

class convert_to_node_tests(TestCase):
    @case({})
    @case({'one': 1})
    def test_creates_node(self, globals_dict):
        inst = Mock()
        xml_node = Mock()
        node_globals = InheritedDict(globals_dict)

        node = convert_to_node(inst, xml_node, node_globals=node_globals)

        msg = 'convert_to_node should create InstanceNode'
        self.assertIsInstance(node, InstanceNode, msg)

        msg = 'convert_to_node should pass globals'
        self.assertEqual(node_globals, node_globals, msg)

class create_node_tests(TestCase):
    @case('pyviews.core.node', 'Node', Node, {})
    @case('pyviews.code', 'Code', Code, {'parent_node': Node(None)})
    def test_creates_node(self, namespace, tag, node_type, init_args):
        xml_node = XmlNode(namespace, tag)

        node = create_node(xml_node, **init_args)

        msg = 'create_node should create instance using namespace as module and tag name as class name'
        self.assertIsInstance(node, node_type, msg)

    @case('pyviews.core.node', 'UnknownNode')
    @case('pyviews.core.unknownModule', 'Node')
    def test_raises_for_not_existance_module_class(self, namespace, tag):
        xml_node = XmlNode(namespace, tag)

        msg = 'create_node should raise in case module or class cannot be imported'
        with self.assertRaises(RenderingError, msg=msg):
            create_node(xml_node)

    @case('pyviews.core.observable', 'Observable', Observable)
    @case('pyviews.core.ioc', 'Services', Services)
    def test_creates_instance_node(self, namespace, tag, inst_type):
        xml_node = XmlNode(namespace, tag)

        node = create_node(xml_node)

        msg = 'create_node should create instance node'
        self.assertIsInstance(node, InstanceNode, msg)

        msg = 'create_node should create instance using namespace as module and tag name as class name'
        self.assertIsInstance(node.instance, inst_type, msg)
