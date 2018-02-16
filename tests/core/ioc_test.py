from unittest import TestCase, main
from unittest.mock import Mock, call
from pyviews.core import ioc

class ContainerTests(TestCase):
    def setUp(self):
        self.container = ioc.Container()

    def test_should_store_dependency(self):
        one = object()
        two = object()
        three = object()
        self.container.register('key', lambda: one)
        self.container.register('paramed', lambda: two)
        self.container.register('paramed', lambda: three, 1)

        msg = 'Registered dependency should be returned by container'
        self.assertEqual(self.container.get('key'), one, msg)

        msg = 'Default dependency should be returned by container with None parameter'
        self.assertEqual(self.container.get('paramed'), two, msg)

        msg = 'Registered with parameter dependency should be returned by container with passed parameter'
        self.assertEqual(self.container.get('paramed', 1), three, msg)

    def test_last_dependency(self):
        one = object()
        two = object()
        self.container.register('key', lambda: one)
        self.container.register('key', lambda: two)
        self.container.register('paramed', lambda: one, 1)
        self.container.register('paramed', lambda: two, 1)

        msg = 'Last dependency should be registered for the same key'
        self.assertEqual(self.container.get('key'), two, msg)

        msg = 'Last dependency should be registered for the same key and parameter'
        self.assertEqual(self.container.get('paramed', 1), two, msg)

    def test_register_raises(self):
        msg = 'Denendency initializer should be callable'
        with self.assertRaises(ioc.DependencyError, msg=msg):
            self.container.register('key', object())

    def test_get_raises(self):
        msg = 'Container should raise exception for not existent dependency'
        with self.assertRaises(ioc.DependencyError, msg=msg):
            self.container.get('key')

    def test_get_params_raises(self):
        msg = 'Container should raise exception for not existent dependency'
        with self.assertRaises(ioc.DependencyError, msg=msg):
            self.container.get('new key')

        self.container.register('key', lambda: 1)
        with self.assertRaises(ioc.DependencyError, msg=msg):
            self.container.get('key', 'param')

    def test_self_registration(self):
        registered_container = self.container.get('container')
        msg = 'Container should register himself with key "Container"'
        self.assertEqual(registered_container, self.container, msg=msg)

class WrappersTests(TestCase):
    def setUp(self):
        self._initial_container = ioc.CONTAINER
        ioc.CONTAINER = Mock()
        ioc.CONTAINER.register = Mock()

    def tearDown(self):
        ioc.CONTAINER = self._initial_container

    def test_register(self):
        one = object()
        name = 'name'
        param = 'param'

        ioc.register(name, one, param)

        msg = 'register method should pass same parameters to CONTAINER.register'
        self.assertEqual(ioc.CONTAINER.register.call_args, call(name, one, param), msg=msg)

    def test_register_value(self):
        one = object()
        name = 'name'
        param = 'param'

        ioc.register_value(name, one, param)

        args = ioc.CONTAINER.register.call_args[0]

        actual = (
            args[0],
            args[1](),
            args[2])
        msg = 'register_value should wrap value to callbale that returns the value'
        self.assertEqual(actual, (name, one, param), msg=msg)

class InjectTests(TestCase):
    def test_inject(self):
        one = object()
        two = lambda: one
        ioc.register_value('one', one)
        ioc.register_value('two', two)

        msg = 'inject should pass dependencies as optional parameters'
        self.assertEqual(self._get_default_injected(), (one, two), msg=msg)
        self.assertEqual(self._get_kwargs_injected(), (one, two), msg=msg)

    @ioc.inject('one', 'two')
    def _get_default_injected(self, one=None, two=None):
        return (one, two)

    @ioc.inject('one', 'two')
    def _get_kwargs_injected(self, **kwargs):
        return (kwargs['one'], kwargs['two'])

if __name__ == '__main__':
    main()
