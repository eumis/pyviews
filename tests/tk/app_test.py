from unittest import TestCase, main
from tests.utility import case
from pyviews.core import ioc
from pyviews.tk import app

class TestIocDependenciesaa(TestCase):
    @case('convert_to_node', app.convert_to_node)
    def test_dependency(self, key, expected):
        actual = ioc.CONTAINER.get(key)
        msg = 'app module should register default for ' + key
        self.assertEqual(actual, expected, msg=msg)

if __name__ == '__main__':
    main()
