from unittest.mock import patch, Mock, call

from injectool import make_default, add_singleton
from pytest import mark, fixture

from pyviews.core import render
from pyviews.rendering import views, render_view
from pyviews.rendering.common import RenderingContext


@fixture
def render_view_fixture(request):
    with make_default('render_view'):
        with patch(f'{views.__name__}.get_view_root') as get_view_root_mock:
            xml_node = Mock()
            get_view_root_mock.side_effect = lambda name: xml_node
            node = Mock()
            add_singleton(render, Mock(return_value=node))
            add_singleton('views_folder', 'folder')

            request.cls.xml_node = xml_node
            request.cls.node = node
            request.cls.get_view_root = get_view_root_mock
            yield get_view_root_mock


@mark.usefixtures('render_view_fixture')
class RenderViewTests:
    """render_view tests"""

    @mark.parametrize('view_name', ['view'])
    def test_renders_root(self, view_name):
        """should render view root"""
        context = RenderingContext()

        actual = render_view(view_name, context)

        assert actual == self.node
        assert self.get_view_root.call_args == call(view_name)
