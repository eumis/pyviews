from unittest.mock import Mock

from injectool import SingletonResolver, add_resolver
from pytest import fixture, mark, raises

from pyviews.code import Code
from pyviews.core import XmlNode, Node
from pyviews.rendering2.common import RenderingContext
from pyviews.rendering2.iteration import RenderingIterator, render
from pyviews.rendering2.pipeline import RenderingPipeline, RenderingItem


@fixture
def rendering_iterator_fixture(request):
    root = Mock()
    iterator = RenderingIterator(root)

    request.cls.root = root
    request.cls.iterator = iterator


@mark.usefixtures('rendering_iterator_fixture')
class RenderingIteratorTests:
    def test_uses_root(self):
        actual = next(self.iterator)

        assert actual == self.root

    def test_raises_stop_iteration(self):
        next(self.iterator)

        with raises(StopIteration):
            next(self.iterator)

    @mark.parametrize('items', [
        [Mock()],
        [Mock(), Mock()],
        [Mock(), Mock(), Mock()]
    ])
    def test_inserts_adds_items(self, items):
        next(self.iterator)

        self.iterator.insert(items)

        actual = list(self.iterator)
        assert actual == items

    @mark.parametrize('items', [
        [Mock()],
        [Mock(), Mock()],
        [Mock(), Mock(), Mock()]
    ])
    def test_inserts_after_current(self, items):
        self.iterator.insert(items)

        actual = list(self.iterator)
        assert actual == items + [self.root]


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
    def test_returns_created_node(self, namespace, tag, node_type, init_args):
        """should return node created by pipeline"""
        context = RenderingContext(init_args)
        context.xml_node = XmlNode(namespace, tag)
        self._set_pipeline(context.xml_node, RenderingPipeline())

        node = render(context)

        assert isinstance(node, node_type)
        assert node.xml_node == context.xml_node

    def test_runs_child_pipelines(self):
        """should run child pipelines"""
        child_pipeline, child_context = Mock(), RenderingContext()

        def pipe(_, __, render_items):
            render_items([RenderingItem(child_pipeline, child_context)])

        self._set_pipeline(self.xml_node, RenderingPipeline([pipe]))

        render(self.context)

        assert child_pipeline.run.call_args[0][0] == child_context
