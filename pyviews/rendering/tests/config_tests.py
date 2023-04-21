from os.path import abspath

from injectool import resolve
from injectool.core import Container
from pytest import mark

from pyviews.rendering.config import use_rendering


@mark.usefixtures('container_fixture')
class UseRenderingTests:
    """use_rendering() tests"""

    container: Container

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
