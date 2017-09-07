from unittest import TestCase, main
from tests.utility import case
from pyviews.core import reflection as tested

class SomeObject:
    def __init__(self, one, two=None):
        self.one = one
        self.two = two

from tests.core.reflection_test import SomeObject

class TestReflection(TestCase):
    @case('tests.core.reflection_test', 'SomeObject', (1,), SomeObject(1))
    @case('tests.core.reflection_test', 'SomeObject', (1, 2), SomeObject(1, 2))
    def test_create_inst(self, module_name, class_name, args, expected):
        actual = tested.create_inst(module_name, class_name, args)

        self.assertIsInstance(actual, SomeObject, 'create_inst should return right object type')
        self.assertEqual(actual.one, expected.one, 'create_inst should pass parameters to constructor')
        self.assertEqual(actual.two, expected.two, 'create_inst should pass parameters to constructor')

    @case(('', 'SomeObject'), ImportError)
    @case(('tests.core.reflection_test', 'AnotherObject'), AttributeError)
    def test_create_inst_raises(self, args, error):
        with self.assertRaises(error, msg='create_inst should raise exception in case not existent module or class'):
            tested.create_inst(*args)

def raise_(ex):
    raise ex

if __name__ == '__main__':
    main()
