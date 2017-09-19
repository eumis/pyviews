from unittest import TestCase, main
from tests.utility import case
from pyviews.common import reflection as tested
from pyviews.common import ioc

class SomeObject:
    def __init__(self, one, two=None):
        self.one = one
        self.two = two

from tests.reflection_test import SomeObject

class TestReflection(TestCase):
    def setUp(self):
        ioc.register_value('event_key', 'event')

    @case(('tests.reflection_test', 'SomeObject'), (1,), SomeObject(1))
    @case(('tests.reflection_test', 'SomeObject'), (1, 2), SomeObject(1, 2))
    def test_create_inst(self, class_path, args, expected):
        params = class_path + args
        actual = tested.create_inst(*params)

        self.assertIsInstance(actual, SomeObject)
        self.assertEqual(actual.one, expected.one)
        self.assertEqual(actual.two, expected.two)

    @case(('', 'SomeObject'), ImportError)
    @case(('tests.reflection_test', 'AnotherObject'), AttributeError)
    def test_create_inst_raises(self, args, error):
        with self.assertRaises(error):
            tested.create_inst(*args)

    @case(lambda: raise_(ValueError))
    @case(lambda event: raise_(ValueError))
    def test_get_event_handler(self, command):
        handler = tested.get_event_handler(command)
        with self.assertRaises(ValueError):
            handler(object())

    def test_get_event_handler_event(self):
        expected = object()
        handler = tested.get_event_handler(lambda event, ex=expected: self.assertEqual(event, ex))
        handler(expected)

def raise_(ex):
    raise ex

if __name__ == '__main__':
    main()
