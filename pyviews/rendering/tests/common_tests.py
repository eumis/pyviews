from unittest.mock import Mock

from pytest import mark, fixture

from pyviews.core import InheritedDict, Node
from pyviews.rendering.common import RenderingContext


@fixture
def rendering_context_fixture(request):
    request.cls.context = RenderingContext()


@mark.usefixtures('rendering_context_fixture')
class RenderingContextTests:
    """RenderingContext tests"""

    def test_node_globals(self):
        """node_globals property should use key 'node_globals'"""
        value = InheritedDict()

        self.context.node_globals = value

        assert self.context.node_globals == value
        assert self.context['node_globals'] == value

    def test_parent_node(self):
        """parent_node property should use key 'parent_node'"""
        value = Node(Mock())

        self.context.parent_node = value

        assert self.context.parent_node == value
        assert self.context['parent_node'] == value
