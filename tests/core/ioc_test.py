from unittest import TestCase, main
from pyviews.core import ioc

class TestContainer(TestCase):
    def setUp(self):
        self.container = ioc.Container()

    def test_should_store_dependency(self):
        one = object()
        two = object()
        three = object()
        self.container.register('key', lambda: one)
        self.container.register('paramed', lambda: two)
        self.container.register('paramed', lambda: three, 1)

        self.assertEqual(self.container.get('key'), one, \
                         'Registered dependency should be returned by container')
        self.assertEqual(self.container.get('paramed'), two, \
                         'Default dependency should be returned by container with None parameter')
        self.assertEqual(self.container.get('paramed', 1), three, \
                         'Registered with parameter dependency should be returned by container with passed parameter')

    def test_should_store_last_dependency(self):
        one = object()
        two = object()
        self.container.register('key', lambda: one)
        self.container.register('key', lambda: two)
        self.container.register('paramed', lambda: one, 1)
        self.container.register('paramed', lambda: two, 1)

        self.assertEqual(self.container.get('key'), two, \
                         'Last dependency should be registered for the same key')
        self.assertEqual(self.container.get('paramed', 1), two, \
                         'Last dependency should be registered for the same key and parameter')

    def test_register_raise_for_non_callable(self):
        with self.assertRaises(Exception, msg='Denendency initializer should be callable'):
            self.container.register('key', object())

    def test_get_raise_for_not_exis_dependency(self):
        with self.assertRaises(Exception, msg='Container should raise exception for not existent dependency'):
            self.container.get('key')

    def test_self_registration(self):
        registered_container = self.container.get('container')

        self.assertEqual(registered_container, self.container, msg='Container should register himself with key "Container"')

class ContainerMock:
    def __init__(self):
        self.passed_params = None

    def register(self, name, initializer, param=None):
        self.passed_params = (name, initializer, param)

class TestWrappers(TestCase):
    def setUp(self):
        self._initial_container = ioc.CONTAINER
        ioc.CONTAINER = ContainerMock()

    def tearDown(self):
        ioc.CONTAINER = self._initial_container

    def test_register(self):
        one = object()
        name = 'name'
        param = 'param'

        ioc.register(name, one, param)

        self.assertEqual(ioc.CONTAINER.passed_params, (name, one, param), 'register method should pass same parameters to CONTAINER.register')

    def test_register_value(self):
        one = object()
        name = 'name'
        param = 'param'

        ioc.register_value(name, one, param)

        actual = (
            ioc.CONTAINER.passed_params[0],
            ioc.CONTAINER.passed_params[1](),
            ioc.CONTAINER.passed_params[2])
        self.assertEqual(actual, (name, one, param), 'register_value should wrap value to callbale that returns the value')

class TestInject(TestCase):
    def test_inject(self):
        one = object()
        two = lambda: one
        ioc.register_value('one', one)
        ioc.register_value('two', two)

        self.assertEqual(self._get_default_injected(), (one, two), 'inject should pass dependencies as optional parameters')
        self.assertEqual(self._get_kwargs_injected(), (one, two), 'inject should pass dependencies as optional parameters')

    @ioc.inject('one', 'two')
    def _get_default_injected(self, one=None, two=None):
        return (one, two)

    @ioc.inject('one', 'two')
    def _get_kwargs_injected(self, **kwargs):
        return (kwargs['one'], kwargs['two'])

if __name__ == '__main__':
    main()
