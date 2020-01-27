from injectool import SingletonResolver, add_resolver
from pytest import fixture, mark

from pyviews.code import Code
from pyviews.core import XmlNode, Node
from pyviews.rendering.common import RenderingContext
from pyviews.rendering.iteration import render
from pyviews.rendering.pipeline import RenderingPipeline


@fixture
def render_fixture(request):
    xml_node = XmlNode('pyviews.core.node', 'Node')
    pipeline = RenderingPipeline()
    pipeline_resolver = SingletonResolver()
    pipeline_resolver.set_value(pipeline, f'{xml_node.namespace}.{xml_node.name}')
    add_resolver(RenderingPipeline, pipeline_resolver)

    request.cls.xml_node = xml_node
    request.cls.pipeline = pipeline
    request.cls.pipeline_resolver = pipeline_resolver
    request.cls.context = RenderingContext({'xml_node': xml_node})


@mark.usefixtures('container_fixture', 'render_fixture')
class RenderTests:
    def _set_pipeline(self, xml_node, pipeline):
        self.pipeline_resolver.set_value(pipeline, f'{xml_node.namespace}.{xml_node.name}')

    @mark.parametrize('namespace, tag, node_type, init_args', [
        ('pyviews.core.node', 'Node', Node, {}),
        ('pyviews.code', 'Code', Code, {'parent_node': Node(XmlNode('', ''))})
    ])
    def test_runs_pipeline(self, namespace, tag, node_type, init_args):
        """should run pipeline and return node created by pipeline"""
        context = RenderingContext(init_args)
        context.xml_node = XmlNode(namespace, tag)
        self._set_pipeline(context.xml_node, RenderingPipeline())

        node = render(context)

        assert isinstance(node, node_type)
        assert node.xml_node == context.xml_node
