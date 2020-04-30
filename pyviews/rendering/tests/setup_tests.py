from os.path import abspath

from injectool import resolve, SingletonResolver
from pytest import mark

from pyviews.rendering import RenderingPipeline
from pyviews.rendering.setup import use_rendering


@mark.usefixtures('container_fixture')
class UseRenderingTests:
    @staticmethod
    def test_views_folder():
        """should add views_folder dependency"""
        use_rendering()

        assert resolve('views_folder') == abspath('views')

    @staticmethod
    def test_views_extension():
        """should add view_ext dependency"""
        use_rendering()

        assert resolve('view_ext') == 'xml'

    def test_rendering_pipeline(self):
        """should add singleton resolver for RenderingPipeline"""
        use_rendering()

        assert isinstance(self.container.get_resolver(RenderingPipeline), SingletonResolver)
