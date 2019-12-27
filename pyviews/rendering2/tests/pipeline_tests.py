from unittest.mock import Mock, call

from injectool import SingletonResolver, add_resolver
from pytest import mark, fixture, raises

from pyviews.code import Code
from pyviews.core import Node, XmlNode, Observable, InstanceNode, xml
from pyviews.rendering2.common import RenderingContext, RenderingError
from pyviews.rendering2.pipeline import RenderingPipeline, get_pipeline, create_instance, get_type


class Inst:
    def __init__(self, xml_node, parent_node):
        self.xml_node = xml_node
        self.parent_node = parent_node

    def __eq__(self, other):
        return self.xml_node == other.xml_node and self.parent_node == other.parent_node


class InstReversed:
    def __init__(self, parent_node, xml_node):
        self.xml_node = xml_node
        self.parent_node = parent_node

    def __eq__(self, other):
        return self.xml_node == other.xml_node and self.parent_node == other.parent_node


class SecondInst:
    def __init__(self, xml_node, parent_node=None):
        self.xml_node = xml_node
        self.parent_node = parent_node

    def __eq__(self, other):
        return self.xml_node == other.xml_node and self.parent_node == other.parent_node


class ThirdInst:
    def __init__(self, xml_node=None, parent_node=None):
        self.xml_node = xml_node
        self.parent_node = parent_node

    def __eq__(self, other):
        return self.xml_node == other.xml_node and self.parent_node == other.parent_node


class FourthInst:
    def __init__(self, xml_node, *_, parent_node=None, **__):
        self.xml_node = xml_node
        self.parent_node = parent_node

    def __eq__(self, other):
        return self.xml_node == other.xml_node and self.parent_node == other.parent_node


class InstWithKwargs:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


@fixture
def pipeline_fixture(request):
    xml_node = XmlNode('pyviews.core.node', 'Node')
    request.cls.context = RenderingContext({'xml_node': xml_node})
    request.cls.pipeline = RenderingPipeline()


@mark.usefixtures('container_fixture', 'pipeline_fixture')
class RenderingPipelineTests:
    @mark.parametrize('namespace, tag, node_type, init_args', [
        ('pyviews.core.node', 'Node', Node, {}),
        ('pyviews.code', 'Code', Code, {'parent_node': Node(XmlNode('', ''))})
    ])
    def test_creates_node(self, namespace, tag, node_type, init_args):
        """should create node using namespace as module and tag name as node class name"""
        context = RenderingContext(init_args)
        context.xml_node = XmlNode(namespace, tag)

        node = self.pipeline.run(context, Mock())

        assert isinstance(node, node_type)
        assert node.xml_node == context.xml_node

    @mark.parametrize('namespace, tag', [
        ('pyviews.core.node', 'UnknownNode'),
        ('pyviews.core.unknownModule', 'Node')
    ])
    def test_raises_for_invalid_path(self, namespace, tag):
        """should raise in case module or class cannot be imported"""
        xml_node = XmlNode(namespace, tag)

        with raises(RenderingError):
            self.pipeline.run(RenderingContext({'xml_node': xml_node}), Mock())

    @mark.parametrize('namespace, tag, inst_type', [
        ('pyviews.core.observable', 'Observable', Observable),
        (__name__, 'InstWithKwargs', InstWithKwargs)
    ])
    def test_creates_instance_node(self, namespace, tag, inst_type):
        """should create instance and wrap it with InstanceNode"""
        xml_node = XmlNode(namespace, tag)

        node = self.pipeline.run(RenderingContext({'xml_node': xml_node}), Mock())

        assert isinstance(node, InstanceNode)
        assert isinstance(node.instance, inst_type)

    @mark.parametrize('pipes_count', [0, 1, 5])
    def test_calls_pipes(self, pipes_count):
        """Should call pipes"""
        pipes = [Mock() for _ in range(pipes_count)]
        pipeline = RenderingPipeline(pipes)
        render_items = Mock()

        node = pipeline.run(self.context, render_items)

        for pipe in pipes:
            assert pipe.call_args == call(node, self.context, render_items)


class GetTypeTests:
    """get_type() function tests"""

    @staticmethod
    @mark.parametrize('xml_node, expected', [
        (XmlNode(__name__, 'Inst'), Inst),
        (XmlNode('pyviews.core.observable', 'Observable'), Observable),
        (XmlNode(__name__, 'SecondInst'), SecondInst),
        (XmlNode('pyviews.core.node', 'Node'), Node)
    ])
    def test_returns_type(xml_node, expected):
        """should return type or module for xml_node"""
        actual = get_type(xml_node)

        assert actual == expected

    @staticmethod
    @mark.parametrize('xml_node', [
        (XmlNode(__name__, 'UnknownType')),
        (XmlNode('pyviews.core.observable', 'SomeClass')),
        (XmlNode('pyviews.some_module.node', 'Node'))
    ])
    def test_raises_for_not_existing_type(xml_node):
        """should raise RenderingError for type failed to import"""
        with raises(RenderingError):
            get_type(xml_node)


class CreateInstanceTests:
    """create_instance() function tests"""

    @staticmethod
    @mark.parametrize('inst_type, init_args, expected', [
        (Inst, {'xml_node': 1, 'parent_node': 'node'}, Inst(1, 'node')),
        (InstReversed, {'xml_node': 1, 'parent_node': 'node'}, InstReversed('node', 1)),
        (SecondInst, {'xml_node': 1, 'parent_node': 'node'}, SecondInst(1, parent_node='node')),
        (SecondInst, {'xml_node': 1}, SecondInst(1)),
        (ThirdInst, {'xml_node': 1, 'parent_node': 'node'}, ThirdInst(xml_node=1, parent_node='node')),
        (ThirdInst, {}, ThirdInst())
    ])
    def test_returns_instance(inst_type, init_args, expected):
        """should create and return instance of passed type"""
        actual = create_instance(inst_type, RenderingContext(init_args))

        assert actual == expected

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
    def test_raises_if_context_misses_argument(inst_type, init_args):
        """should raise RenderingError if there are no required arguments"""
        with raises(RenderingError):
            create_instance(inst_type, RenderingContext(init_args))


@mark.parametrize('inst_type, init_args', [
    (Inst, {'xml_node': 1, 'parent_node': 'node'}),
    (InstReversed, {'xml_node': 1, 'parent_node': 'node'}),
    (SecondInst, {'xml_node': 1, 'parent_node': 'node'}),
    (ThirdInst, {'xml_node': 1, 'parent_node': 'node'})
])
def test_create_inst(inst_type, init_args):
    """should create and return instance of passed type"""
    inst = create_instance(inst_type, RenderingContext(init_args))

    assert isinstance(inst, inst_type)


@mark.usefixtures('container_fixture')
@mark.parametrize('xml_node', [
    XmlNode('pyviews.core.node', 'Node'),
    XmlNode('pyviews.core.observable', 'Observable'),
])
def get_pipeline_tests(xml_node):
    resolver = SingletonResolver()
    add_resolver(RenderingPipeline, resolver)
    pipeline = RenderingPipeline()
    resolver.set_value(pipeline, f'{xml_node.namespace}.{xml_node.name}')

    actual = get_pipeline(xml_node)

    assert actual == pipeline
