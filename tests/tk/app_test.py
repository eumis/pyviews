from os.path import abspath
from unittest import TestCase, main
from tests.utility import case
from pyviews.core import ioc
from pyviews.tk.parsing import convert_to_node
from pyviews.tk.modifiers import set_attr
from pyviews.tk import app

class TestIocDependenciesaa(TestCase):
    @case('convert_to_node', convert_to_node)
    @case('set_attr', set_attr)
    @case('views_folder', abspath('views'))
    @case('view_ext', '.xml')
    def test_dependency(self, key, expected):
        actual = ioc.CONTAINER.get(key)
        msg = 'app module should register default for ' + key
        self.assertEqual(actual, expected, msg=msg)

if __name__ == '__main__':
    main()