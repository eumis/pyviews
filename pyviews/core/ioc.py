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

CONTAINER = Container()

class Scope:
    '''Dependencies scope'''

    _scopes = {}
    _current_scope = None

    def __init__(self, name):
        self._previous_container = None
        self.name = name
        if name not in Scope._scopes:
            Scope._scopes[name] = Container()

    def __enter__(self):
        global CONTAINER
        self._default_container = CONTAINER
        CONTAINER = Scope._scopes[self.name]
        return self

    def __exit__(self, type, value, traceback):
        global CONTAINER
        CONTAINER = self._default_container

def register(key, initializer: callable, param=None):
    '''Adds resolver to global container'''
    CONTAINER.register(key, initializer, param)

def register_single(key, value, param=None):
    '''Generates resolver to return singleton value and adds it to global container'''
    CONTAINER.register(key, lambda: value, param)

def register_func(key, func, param=None):
    '''Generates resolver to return passed function'''
    register_single(key, func, param)

def scope(name):
    '''Calls function with passed scope'''
    def decorate(func):
        return wrap_with_scope(func, name)
    return decorate

def wrap_with_scope(func, scope_name):
    '''Wraps function with scope'''
    return lambda *args, **kwargs: _call_with_scope(func, scope_name, args, kwargs)

def _call_with_scope(func, scope_name, args, kwargs):
    with Scope(scope_name):
        return func(*args, **kwargs)

def inject(*injections):
    '''Resolves dependencies using global container and passed it with optional parameters'''
    def decorate(func):
        def decorated(*args, **kwargs):
            args = list(args)
            keys_to_inject = [name for name in injections if name not in kwargs]
            for key in keys_to_inject:
                kwargs[key] = CONTAINER.get(key)
            return func(*args, **kwargs)
        return decorated
    return decorate
