from unittest.mock import Mock, call

from pytest import fixture, mark, raises

from pyviews import ioc


@fixture
def container_fixture(request):
    request.cls.container = ioc.Container()


@mark.usefixtures('container_fixture')
class ContainerTests:
    def test_register(self):
        """container should register dependencies"""
        one = object()
        two = object()
        three = object()
        four = object()
        self.container.register('key', lambda: one)
        self.container.register('paramed', lambda: two)
        self.container.register('paramed', lambda: three, 1)
        self.container.register_factory('paramed', lambda param: four if param == 2 else None)

        assert self.container.get('key') == one
        assert self.container.get('paramed') == two
        assert self.container.get('paramed', 1) == three
        assert self.container.get('paramed', 2) == four

    def test_last_dependency(self):
        """register() should overwrite dependency"""
        one = object()
        two = object()
        self.container.register('key', lambda: one)
        self.container.register('key', lambda: two)
        self.container.register('paramed', lambda: one, 1)
        self.container.register('paramed', lambda: two, 1)

        assert self.container.get('key') == two
        assert self.container.get('paramed', 1) == two

    def test_register_raises(self):
        """register() should raise error if initializer is not callable"""
        with raises(ioc.DependencyError):
            self.container.register('key', object())

    def test_get_raises(self):
        """Container should raise exception for not existent dependency"""
        with raises(ioc.DependencyError):
            self.container.get('key')

    def test_get_params_raises(self):
        """Container should raise exception for not existent dependency"""
        with raises(ioc.DependencyError):
            self.container.get('new key')

        self.container.register('key', lambda: 1)
        with raises(ioc.DependencyError):
            self.container.get('key', 'param')

    def test_self_registration(self):
        """Container should register himself with key "Container"""
        registered_container = self.container.get('container')

        assert registered_container == self.container


@fixture
def wrappers_fixture(request):
    scope_name = 'WrappersTests'
    request.cls.container = Mock()
    ioc.Scope._scope_containers[scope_name] = request.cls.container
    with ioc.Scope(scope_name) as fixture_scope:
        yield fixture_scope


@mark.usefixtures('wrappers_fixture')
class WrappersTests:
    @staticmethod
    def test_register():
        """register() should pass same parameters to CONTAINER.register"""
        one = object()
        name = 'name'
        param = 'param'

        ioc.register(name, one, param)

        container = ioc.get_current_scope().container
        assert container.register.call_args == call(name, one, param)

    @staticmethod
    def test_register_single():
        """register_single() should wrap value to callbale that returns the value"""
        one = object()
        name = 'name'
        param = 'param'

        ioc.register_single(name, one, param)

        args = ioc.get_current_scope().container.register.call_args[0]

        actual = (
            args[0],
            args[1](),
            args[2])
        assert actual == (name, one, param)

    @staticmethod
    def test_register_func():
        """register_func() should wrap value to callable that returns the value"""
        def one(*one_args): print(one_args)
        name = 'name'
        param = 'param'

        ioc.register_func(name, one, param)

        args = ioc.get_current_scope().container.register.call_args[0]

        actual = (
            args[0],
            args[1](),
            args[2])
        assert actual == (name, one, param)


def test_inject():
    """should pass dependencies as optional parameters"""
    one = object()
    def two(): return one
    ioc.register_single('one', one)
    ioc.register_func('two', two)

    assert _get_default_injected() == (one, two)
    assert _get_kwargs_injected() == (one, two)


@ioc.inject('one', 'two')
def _get_default_injected(one=None, two=None):
    return one, two


@ioc.inject('one', 'two')
def _get_kwargs_injected(**kwargs):
    return kwargs['one'], kwargs['two']


class ScopeTests:
    def test_scope(self):
        """Scope should use own Container for resolving dependencies"""
        ioc.register_single('value', 0)
        with ioc.Scope('one'):
            ioc.register_single('value', 1)
        with ioc.Scope('two'):
            ioc.register_single('value', 2)

        with ioc.Scope('one'):
            assert self._get_injected_value() == 1
        with ioc.Scope('two'):
            assert self._get_injected_value() == 2
        assert self._get_injected_value() == 0

    @staticmethod
    def test_current_scope():
        """Scope should use own Container for resolving dependencies"""
        with ioc.Scope('one') as one_scope:
            assert one_scope == ioc.get_current_scope()
            with ioc.Scope('two') as two_scope:
                assert two_scope == ioc.get_current_scope()
            assert one_scope == ioc.get_current_scope()

    @staticmethod
    def test_wrap_same_scope():
        with ioc.Scope('scope') as outer_scope:
            with ioc.Scope('scope') as inner_scope:
                assert outer_scope != inner_scope
                assert outer_scope == ioc.get_current_scope()
                assert outer_scope.container == inner_scope.container

    def test_inner_scope(self):
        """Scope should use own Container for resolving dependencies if used inside other scope"""
        ioc.register_single('value', 0)
        with ioc.Scope('one'):
            ioc.register_single('value', 1)
            with ioc.Scope('two'):
                ioc.register_single('value', 2)

        with ioc.Scope('one'):
            assert self._get_injected_value() == 1
        with ioc.Scope('two'):
            assert self._get_injected_value() == 2
        assert self._get_injected_value() == 0

    @staticmethod
    @ioc.inject('value')
    def _get_injected_value(value=None):
        return value

    def test_scope_decorator(self):
        """scope decorator should wrap function call with passed scope"""
        ioc.register_single('value', 0)
        with ioc.Scope('one'):
            ioc.register_single('value', 1)
        with ioc.Scope('two'):
            ioc.register_single('value', 2)

        assert self._get_injected_value() == 0
        assert self._get_one_scope_value() == 1
        assert self._get_two_scope_value() == 2

    @staticmethod
    @ioc.scope('one')
    @ioc.inject('value')
    def _get_one_scope_value(value=None):
        return value

    @staticmethod
    @ioc.scope('two')
    @ioc.inject('value')
    def _get_two_scope_value(value=None):
        return value

    def test_wrap_with_scope(self):
        """wrap_with_scope should wrap passed function call with scope"""
        ioc.register_single('value', 0)
        with ioc.Scope('one'):
            ioc.register_single('value', 1)
        with ioc.Scope('two'):
            ioc.register_single('value', 2)

        one = ioc.wrap_with_scope(self._get_injected_value, 'one')
        two = ioc.wrap_with_scope(self._get_injected_value, 'two')

        assert one() == 1
        assert two() == 2

    def test_wrap_with_current_scope(self):
        """wrap_with_scope should wrap passed function call with scope"""
        ioc.register_single('value', 0)
        with ioc.Scope('one'):
            ioc.register_single('value', 1)
            one = ioc.wrap_with_scope(self._get_injected_value)
        with ioc.Scope('two'):
            ioc.register_single('value', 2)
            two = ioc.wrap_with_scope(self._get_injected_value)

        assert one() == 1
        assert two() == 2


class ServicesTests:
    @staticmethod
    def test_injection():
        """services should return registered dependencies"""
        one = object()
        def two(): return one
        ioc.register_single('one', one)
        ioc.register_func('two', two)

        assert ioc.SERVICES.one == one
        assert ioc.SERVICES.two == two

    @staticmethod
    def test_scope_injection():
        """services should return registered dependencies in current scope"""
        one = object()
        two = object()
        with ioc.Scope('one'):
            ioc.register_single('dep', one)
        with ioc.Scope('two'):
            ioc.register_single('dep', two)

        with ioc.Scope('one'):
            assert ioc.SERVICES.dep == one
        with ioc.Scope('two'):
            assert ioc.SERVICES.dep == two

    @staticmethod
    def test_for_():
        """for_ should return services that using passed param"""
        one = object()
        two = object()
        ioc.register_single('dep', one, 'one')
        ioc.register_single('dep', two, 'two')

        assert ioc.SERVICES.for_('one').dep == one
        assert ioc.SERVICES.for_('two').dep == two
