from unittest.mock import Mock

from pytest import mark, fixture

from pyviews.core import InheritedDict, Node, XmlNode
from pyviews.rendering2.common import RenderingContext


@fixture
def rendering_context_fixture(request):
    request.cls.context = RenderingContext()


@mark.usefixtures('rendering_context_fixture')
class RenderingContextTests:
    """RenderingContext tests"""

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
