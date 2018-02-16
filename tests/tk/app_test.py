from os.path import abspath
from unittest import TestCase, main
from tests.utility import case
from pyviews.core import ioc
from pyviews.tk.rendering import convert_to_node
from pyviews.tk.modifiers import set_attr
from pyviews.tk import app

class TestIocDependencies(TestCase):
    def setUp(self):
        self._container = ioc.CONTAINER

    @case('convert_to_node', convert_to_node)
    @case('set_attr', set_attr)
    @case('views_folder', abspath('views'))
    @case('view_ext', '.xml')
    def test_dependency(self, key, expected):
        ioc.CONTAINER = ioc.Container()
        app.register_dependencies()
        actual = ioc.CONTAINER.get(key)
        msg = 'app module should register default for {0}'.format(key)
        self.assertEqual(actual, expected, msg=msg)

    def tearDown(self):
        ioc.CONTAINER = self._container

if __name__ == '__main__':
    main()
