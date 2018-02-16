from unittest import TestCase, main
from tests.utility import case
from pyviews.rendering.converters import to_int

class ConvertersTests(TestCase):
    @case('1', 1)
    @case(' 1 ', 1)
    @case('25', 25)
    @case('', None)
    @case(' ', None)
    @case(None, None)
    def test_to_int(self, value, expected):
        msg = 'to_int should convert value to int'
        self.assertEqual(to_int(value), expected, msg)

    @case('2 5')
    @case('1a')
    @case('1.1')
    @case('1.9')
    @case('one')
    def test_to_int_raises(self, value):
        msg = 'to_int should raise exception for invalid value'
        with self.assertRaises(ValueError, msg=msg):
            to_int(value)

if __name__ == '__main__':
    main()
