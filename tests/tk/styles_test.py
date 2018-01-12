from unittest import TestCase, main
from unittest.mock import call, Mock
from tests.utility import case
from pyviews.tk.styles import StyleItem

class StyleItemTest(TestCase):
    @case('key', 1)
    @case('asdf', None)
    @case('', None)
    @case('', 1)
    def test_apply_should_call_modifier(self, name, value):
        modifier = Mock()
        item = StyleItem(modifier, name, value)
        node = Mock()

        item.apply(node)

        msg = 'apply should call passed modifier with parameters'
        self.assertEqual(modifier.call_args, call(node, name, value))

class StyleTest(TestCase):
    pass

if __name__ == '__main__':
    main()
