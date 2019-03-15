'''Dependency injection implementation'''

from threading import local as thread_local
from .common import CoreError

class DependencyError(CoreError):
    '''Base for ioc errors'''

class Container:
    '''Container for dependencies'''
    def __init__(self):
        self._initializers = {}
        self._factories = {}
        self.register('container', lambda: self)

    def register(self, key, initializer: callable, param=None):
        '''Add resolver to container'''
        if not callable(initializer):
            raise DependencyError('Initializer {0} is not callable'.format(initializer))
        if key not in self._initializers:
            self._initializers[key] = {}
        self._initializers[key][param] = initializer

    def register_factory(self, key, initializer):
        '''Add initializer that called with passed param'''
        self._factories[key] = initializer

    def get(self, key, param=None):
        '''Resolve dependecy'''
        try:
            return self._initializers[key][param]()
        except KeyError:
            if key in self._factories:
                return self._factories[key](param)
            raise DependencyError('Dependency "{0}" is not found'.format(key))

_THREAD_LOCAL = thread_local()

class Scope:
    '''Dependencies scope'''

    _scope_containers = {}

    def __init__(self, name):
        self._previous_scope = None
        self.name = name
        if name not in Scope._scope_containers:
            Scope._scope_containers[name] = Container()

    @property
    def container(self):
        '''Returns scope container'''
        return Scope._scope_containers[self.name]

    def __enter__(self):
        try:
            self._previous_scope = get_current_scope()
        except DependencyError:
            self._previous_scope = None
        if not self._previous_scope or self.name != self._previous_scope.name:
            self.container.register('scope', lambda: self)
            set_current_scope(self)
        return self

    def __exit__(self, exc_type, value, traceback):
        set_current_scope(self._previous_scope)

def get_current_scope() -> Scope:
    '''return current scope'''
    current_scope = getattr(_THREAD_LOCAL, 'current_scope', None)
    if current_scope is None:
        raise DependencyError("ioc is not set up for current thread")
    return _THREAD_LOCAL.current_scope

def set_current_scope(current_scope: Scope):
    '''sets current scope'''
    _THREAD_LOCAL.current_scope = current_scope

Scope('').__enter__()

def register(key, initializer: callable, param=None):
    '''Adds resolver to global container'''
    get_current_scope().container.register(key, initializer, param)

def register_single(key, value, param=None):
    '''Generates resolver to return singleton value and adds it to global container'''
    get_current_scope().container.register(key, lambda: value, param)

def register_func(key, func, param=None):
    '''Generates resolver to return passed function'''
    register_single(key, func, param)

def scope(name):
    '''Calls function with passed scope'''
    def _decorate(func):
        return wrap_with_scope(func, name)
    return _decorate

def wrap_with_scope(func, scope_name=None):
    '''Wraps function with scope. If scope_name is None current scope is used'''
    if scope_name is None:
        scope_name = get_current_scope().name
    return lambda *args, scope=scope_name, **kwargs: \
           _call_with_scope(func, scope, args, kwargs)

def _call_with_scope(func, scope_name, args, kwargs):
    with Scope(scope_name):
        return func(*args, **kwargs)

class Services:
    '''Provides interface for getting dependencies'''
    def __init__(self, param=None):
        self._param = param

    def __getattr__(self, key):
        return get_current_scope().container.get(key, self._param)

    @staticmethod
    def for_(param) -> 'Services':
        '''Returns container services that uses passed param'''
        return Services(param)


SERVICES = Services()

def inject(*injections):
    '''Resolves dependencies using global container and passed it with optional parameters'''
    def _decorate(func):
        def _decorated(*args, **kwargs):
            args = list(args)
            keys_to_inject = [name for name in injections if name not in kwargs]
            for key in keys_to_inject:
                kwargs[key] = get_current_scope().container.get(key)
            return func(*args, **kwargs)
        return _decorated
    return _decorate
