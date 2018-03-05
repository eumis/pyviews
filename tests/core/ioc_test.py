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
        container = Mock()
        container = Mock()
        ioc.Scope._scope_containers['WrappersTests'] = container

    @ioc.scope('WrappersTests')
    def test_register(self):
        one = object()
        name = 'name'
        param = 'param'

        ioc.register(name, one, param)

        msg = 'register method should pass same parameters to CONTAINER.register'
        container = ioc.Scope.Current.container
        self.assertEqual(container.register.call_args, call(name, one, param), msg=msg)

    @ioc.scope('WrappersTests')
    def test_register_single(self):
        one = object()
        name = 'name'
        param = 'param'

        ioc.register_single(name, one, param)

        args = ioc.Scope.Current.container.register.call_args[0]

        actual = (
            args[0],
            args[1](),
            args[2])
        msg = 'register_single should wrap value to callbale that returns the value'
        self.assertEqual(actual, (name, one, param), msg=msg)

    @ioc.scope('WrappersTests')
    def test_register_func(self):
        one = lambda *args: print(args)
        name = 'name'
        param = 'param'

        ioc.register_func(name, one, param)

        args = ioc.Scope.Current.container.register.call_args[0]

        actual = (
            args[0],
            args[1](),
            args[2])
        msg = 'register_func should wrap value to callbale that returns the value'
        self.assertEqual(actual, (name, one, param), msg=msg)

class InjectTests(TestCase):
    def test_inject(self):
        one = object()
        two = lambda: one
        ioc.register_single('one', one)
        ioc.register_func('two', two)

        msg = 'inject should pass dependencies as optional parameters'
        self.assertEqual(self._get_default_injected(), (one, two), msg=msg)
        self.assertEqual(self._get_kwargs_injected(), (one, two), msg=msg)

    @ioc.inject('one', 'two')
    def _get_default_injected(self, one=None, two=None):
        return (one, two)

    @ioc.inject('one', 'two')
    def _get_kwargs_injected(self, **kwargs):
        return (kwargs['one'], kwargs['two'])

class ScopeTests(TestCase):
    def test_scope(self):
        ioc.register_single('value', 0)
        with ioc.Scope('one'):
            ioc.register_single('value', 1)
        with ioc.Scope('two'):
            ioc.register_single('value', 2)

        msg = 'Scope should use own Container for resolving dependencies'
        with ioc.Scope('one'):
            self.assertEqual(self._get_injected_value(), 1, msg)
        with ioc.Scope('two'):
            self.assertEqual(self._get_injected_value(), 2, msg)
        self.assertEqual(self._get_injected_value(), 0, msg)

    def test_current_scope(self):
        msg = 'Scope should use own Container for resolving dependencies'
        with ioc.Scope('one') as one_scope:
            self.assertEqual(one_scope, ioc.Scope.Current, msg)
            with ioc.Scope('two') as two_scope:
                self.assertEqual(two_scope, ioc.Scope.Current, msg)
            self.assertEqual(one_scope, ioc.Scope.Current, msg)

    def test_wrap_same_scope(self):
        with ioc.Scope('scope') as outer_scope:
            with ioc.Scope('scope') as inner_scope:
                msg = '__enter__ should return new Scope object'
                self.assertNotEqual(outer_scope, inner_scope, msg)

                msg = 'Outer scope should be current'
                self.assertEqual(outer_scope, ioc.Scope.Current, msg)

                msg = 'Scopes with same name should use same container'
                self.assertEqual(outer_scope.container, inner_scope.container, msg)

    def test_inner_scope(self):
        ioc.register_single('value', 0)
        with ioc.Scope('one'):
            ioc.register_single('value', 1)
            with ioc.Scope('two'):
                ioc.register_single('value', 2)

        msg = 'Scope should use own Container for resolving dependencies if used inside other scope'
        with ioc.Scope('one'):
            self.assertEqual(self._get_injected_value(), 1, msg)
        with ioc.Scope('two'):
            self.assertEqual(self._get_injected_value(), 2, msg)
        self.assertEqual(self._get_injected_value(), 0, msg)

    @ioc.inject('value')
    def _get_injected_value(self, value=None):
        return value

    def test_scope_decorator(self):
        ioc.register_single('value', 0)
        with ioc.Scope('one'):
            ioc.register_single('value', 1)
        with ioc.Scope('two'):
            ioc.register_single('value', 2)

        msg = 'scope decorator should wrap function call with passed scope'
        self.assertEqual(self._get_injected_value(), 0, msg)
        self.assertEqual(self._get_one_scope_value(), 1, msg)
        self.assertEqual(self._get_two_scope_value(), 2, msg)

    @ioc.scope('one')
    @ioc.inject('value')
    def _get_one_scope_value(self, value=None):
        return value

    @ioc.scope('two')
    @ioc.inject('value')
    def _get_two_scope_value(self, value=None):
        return value

    def test_wrap_with_scope(self):
        ioc.register_single('value', 0)
        with ioc.Scope('one'):
            ioc.register_single('value', 1)
        with ioc.Scope('two'):
            ioc.register_single('value', 2)

        one = ioc.wrap_with_scope(self._get_injected_value, 'one')
        two = ioc.wrap_with_scope(self._get_injected_value, 'two')

        msg = 'wrap_with_scope should wrap passed function call with scope'
        self.assertEqual(one(), 1, msg)
        self.assertEqual(two(), 2, msg)

    def test_wrap_with_current_scope(self):
        ioc.register_single('value', 0)
        with ioc.Scope('one'):
            ioc.register_single('value', 1)
            one = ioc.wrap_with_scope(self._get_injected_value)
        with ioc.Scope('two'):
            ioc.register_single('value', 2)
            two = ioc.wrap_with_scope(self._get_injected_value)

        msg = 'wrap_with_scope should wrap passed function call with scope'
        self.assertEqual(one(), 1, msg)
        self.assertEqual(two(), 2, msg)

if __name__ == '__main__':
    main()
