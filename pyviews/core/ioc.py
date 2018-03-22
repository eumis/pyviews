'''Dependency injection implementation'''

from pyviews.core import CoreError

class DependencyError(CoreError):
    '''Base for ioc errors'''
    pass

class Container:
    '''Container for dependencies'''
    def __init__(self):
        self._initializers = {}
        self.register('container', lambda: self)

    def register(self, key, initializer: callable, param=None):
        '''Add resolver to container'''
        if not callable(initializer):
            raise DependencyError('Initializer {0} is not callable'.format(initializer))
        if key not in self._initializers:
            self._initializers[key] = {}
        self._initializers[key][param] = initializer

    def get(self, key, param=None):
        '''Resolve dependecy'''
        if key not in self._initializers or param not in self._initializers[key]:
            raise DependencyError('Dependency "{0}" is not found'.format(key))
        return self._initializers[key][param]()

class Scope:
    '''Dependencies scope'''

    _scope_containers = {}
    Current = None

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
        self._previous_scope = Scope.Current
        if self.name != Scope.Current.name:
            self.container.register('scope', lambda: self)
            Scope.Current = self
        return self

    def __exit__(self, exc_type, value, traceback):
        Scope.Current = self._previous_scope

Scope.Current = Scope('')
Scope.Current.__enter__()

def register(key, initializer: callable, param=None):
    '''Adds resolver to global container'''
    Scope.Current.container.register(key, initializer, param)

def register_single(key, value, param=None):
    '''Generates resolver to return singleton value and adds it to global container'''
    Scope.Current.container.register(key, lambda: value, param)

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
        scope_name = Scope.Current.name
    return lambda *args, **kwargs: _call_with_scope(func, scope_name, args, kwargs)

def _call_with_scope(func, scope_name, args, kwargs):
    with Scope(scope_name):
        return func(*args, **kwargs)

def inject(*injections):
    '''Resolves dependencies using global container and passed it with optional parameters'''
    def _decorate(func):
        def _decorated(*args, **kwargs):
            args = list(args)
            keys_to_inject = [name for name in injections if name not in kwargs]
            for key in keys_to_inject:
                kwargs[key] = Scope.Current.container.get(key)
            return func(*args, **kwargs)
        return _decorated
    return _decorate
