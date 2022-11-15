from unittest.mock import Mock

from pytest import mark, fixture

from pyviews.core import InheritedDict, Node, XmlNode
from pyviews.rendering.common import RenderingContext, use_context, get_rendering_context, pass_rendering_context


@fixture
def rendering_context_fixture(request):
    request.cls.context = RenderingContext()


@mark.usefixtures('rendering_context_fixture')
class RenderingContextTests:
    """RenderingContext tests"""

    context: RenderingContext

    def test_node_globals(self):
        """node_globals property should use key 'node_globals'"""
        value = InheritedDict()
        init_value = self.context.node_globals

        self.context.node_globals = value

        assert init_value is None
        assert self.context.node_globals == value
        assert self.context['node_globals'] == value

    def test_parent_node(self):
        """parent_node property should use key 'parent_node'"""
        value = Node(Mock())
        init_value = self.context.parent_node

        self.context.parent_node = value

        assert init_value is None
        assert self.context.parent_node == value
        assert self.context['parent_node'] == value

    def test_xml_node(self):
        """xml_node property should use key 'xml_node'"""
        value = XmlNode('namespace', 'name')
        init_value = self.context.xml_node

        self.context.xml_node = value

        assert init_value is None
        assert self.context.xml_node == value
        assert self.context['xml_node'] == value


def test_use_context():
    """Should use passed rendering context in context scope"""
    one, two, three = RenderingContext(), RenderingContext(), RenderingContext()

    with use_context(one):
        with use_context(two):
            with use_context(three):
                assert get_rendering_context() is three
            assert get_rendering_context() is two
        assert get_rendering_context() is one
    assert get_rendering_context() is None


def test_pass_rendering_context():
    """Should pass rendering context as default argument"""

    @pass_rendering_context
    def get_current_context(rendering_context: RenderingContext = None):
        return rendering_context

    with use_context(RenderingContext()) as ctx:
        assert get_current_context() is ctx
    assert get_current_context() is None
