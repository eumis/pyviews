from unittest.mock import Mock

from pytest import mark, raises

from pyviews.core import XmlNode, Node, InstanceNode
from pyviews.core import InheritedDict, Observable
from pyviews.code import Code
from pyviews.rendering.common import RenderingError
from pyviews.rendering.node import get_init_args, convert_to_node
from pyviews.rendering.node import create_node, create_inst


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
    def __init__(self, xml_node, *_, parent_node=None, **__):
        self.xml_node = xml_node
        self.parent_node = parent_node


class InstWithKwargs:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class GetInitArgsTests:
    """get_init_args() tests"""

    @staticmethod
    @mark.parametrize('inst_type, init_args, args, kwargs, add_kwargs', [
        (Inst, {'xml_node': 1, 'parent_node': 'node'}, [1, 'node'], {}, True),
        (Inst, {'xml_node': 1, 'parent_node': 'node'}, [1, 'node'], {}, False),
        (InstReversed, {'xml_node': 1, 'parent_node': 'node'}, ['node', 1], {}, True),
        (InstReversed, {'xml_node': 1, 'parent_node': 'node'}, ['node', 1], {}, False),
        (SecondInst, {'xml_node': 1, 'parent_node': 'node'}, [1], {'parent_node': 'node'}, True),
        (SecondInst, {'xml_node': 1, 'parent_node': 'node'}, [1], {'parent_node': 'node'}, False),
        (ThirdInst, {'xml_node': 1, 'parent_node': 'node'}, [], {'xml_node': 1, 'parent_node': 'node'}, True),
        (ThirdInst, {'xml_node': 1, 'parent_node': 'node'}, [], {'xml_node': 1, 'parent_node': 'node'}, False),
        (FourthInst,
         {'xml_node': 1, 'parent_node': 'node', 'some_key': 'value'}, [1],
         {'parent_node': 'node', 'some_key': 'value'}, True),
        (FourthInst,
         {'xml_node': 1, 'parent_node': 'node', 'some_key': 'value'}, [1],
         {'parent_node': 'node'}, False),
        (InstWithKwargs, {'xml_node': 1, 'parent_node': 'node'}, [], {'xml_node': 1, 'parent_node': 'node'}, True),
        (InstWithKwargs, {'xml_node': 1, 'parent_node': 'node'}, [], {}, False)
    ])
    def test_returns_args_kwargs_for_constructor(inst_type, init_args, args, kwargs, add_kwargs):
        """should return args for inst_type constructor"""
        actual_args, actual_kwargs = get_init_args(inst_type, init_args, add_kwargs=add_kwargs)

        assert args == actual_args
        assert kwargs == actual_kwargs

    @staticmethod
    @mark.parametrize('inst_type, init_args', [
        (Inst, {}),
        (Inst, {'xml_node': 1}),
        (Inst, {'parent_node': 'node'}),
        (InstReversed, {'xml_node': 1}),
        (InstReversed, {'parent_node': 'node'}),
        (SecondInst, {}),
        (SecondInst, {'parent_node': 'node'})
    ])
    def test_raises_if_init_args_not_contain_key(inst_type, init_args):
        """should raise RenderingError if there are no required arguments"""
        with raises(RenderingError):
            get_init_args(inst_type, init_args)


@mark.parametrize('inst_type, init_args', [
    (Inst, {'xml_node': 1, 'parent_node': 'node'}),
    (InstReversed, {'xml_node': 1, 'parent_node': 'node'}),
    (SecondInst, {'xml_node': 1, 'parent_node': 'node'}),
    (ThirdInst, {'xml_node': 1, 'parent_node': 'node'})
])
def test_create_inst(inst_type, init_args):
    """should create and return instance of passed type"""
    inst = create_inst(inst_type, **init_args)

    assert isinstance(inst, inst_type)


@mark.parametrize('globals_dict', [
    {},
    {'one': 1}
])
def test_convert_to_node(globals_dict):
    """should create InstanceNode with passed globals"""
    inst = Mock()
    xml_node = Mock()
    node_globals = InheritedDict(globals_dict)

    node = convert_to_node(inst, xml_node, node_globals=node_globals)

    assert isinstance(node, InstanceNode)
    assert node.instance == inst
    assert node.node_globals == node_globals


class CreateNodeTests:
    @staticmethod
    @mark.parametrize('namespace, tag, node_type, init_args', [
        ('pyviews.core.node', 'Node', Node, {}),
        ('pyviews.code', 'Code', Code, {'parent_node': Node(XmlNode('', ''))})
    ])
    def test_creates_node(namespace, tag, node_type, init_args):
        """should create node using namespace as module and tag name as node class name"""
        xml_node = XmlNode(namespace, tag)

        node = create_node(xml_node, **init_args)

        assert isinstance(node, node_type)

    @staticmethod
    @mark.parametrize('namespace, tag', [
        ('pyviews.core.node', 'UnknownNode'),
        ('pyviews.core.unknownModule', 'Node')
    ])
    def test_raises_for_invalid_path(namespace, tag):
        """should raise in case module or class cannot be imported"""
        xml_node = XmlNode(namespace, tag)

        with raises(RenderingError):
            create_node(xml_node)

    @staticmethod
    @mark.parametrize('namespace, tag, inst_type', [
        ('pyviews.core.observable', 'Observable', Observable),
        (__name__, 'InstWithKwargs', InstWithKwargs)
    ])
    def test_creates_instance_node(namespace, tag, inst_type):
        """should create instance and wrap it with InstanceNode"""
        xml_node = XmlNode(namespace, tag)

        node = create_node(xml_node)

        assert isinstance(node, InstanceNode)
        assert isinstance(node.instance, inst_type)
