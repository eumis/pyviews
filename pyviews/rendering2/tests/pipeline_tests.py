from unittest.mock import Mock, call

from pytest import mark, fixture, raises

from pyviews.code import Code
from pyviews.core import Node, XmlNode, Observable, InstanceNode
from pyviews.rendering import RenderingError
from pyviews.rendering2.common import RenderingContext
from pyviews.rendering2.pipeline import RenderingPipeline


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
