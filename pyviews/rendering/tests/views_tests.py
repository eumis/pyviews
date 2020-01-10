from unittest.mock import patch, Mock, call

from injectool import add_singleton
from pytest import mark, fixture
from rx import of

from pyviews.rendering import views
from pyviews.rendering.common import RenderingContext
from pyviews.rendering.iteration import render
from pyviews.rendering.views import render_view


@fixture
def render_view_fixture(request):
    with patch(f'{views.__name__}.get_view_root') as get_view_root_mock:
        xml_node = Mock()
        get_view_root_mock.side_effect = lambda name: xml_node
        node = Mock()
        add_singleton(render, Mock(return_value=of(node)))
        add_singleton('views_folder', 'folder')

        request.cls.xml_node = xml_node
        request.cls.node = node
        request.cls.get_view_root = get_view_root_mock
        yield get_view_root_mock


@mark.usefixtures('container_fixture', 'render_view_fixture')
class RenderViewTests:
    """render_view tests"""

    @mark.parametrize('view_name', ['view'])
    def test_renders_root(self, view_name):
        """should render view root"""
        context = RenderingContext()

        actual = render_view(view_name, context).run()

        assert actual == self.node
        assert self.get_view_root.call_args == call(view_name)
