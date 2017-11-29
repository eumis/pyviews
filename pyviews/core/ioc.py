class Container:
    def __init__(self):
        self._initializers = {}
        self.register('container', lambda: self)

    def register(self, key, initializer: callable, param=None):
        if not callable(initializer):
            raise ValueError('Initializer should be callable', initializer)
        if key not in self._initializers:
            self._initializers[key] = {}
        self._initializers[key][param] = initializer

    def get(self, key, param=None):
        if key not in self._initializers or param not in self._initializers[key]:
            raise KeyError('Dependency with name ' + key + ' is not found')
        return self._initializers[key][param]()

CONTAINER = Container()

def register(key, initializer: callable, param=None):
    CONTAINER.register(key, initializer, param)

def register_value(key, value, param=None):
    CONTAINER.register(key, lambda: value, param)

def inject(*injections):
    def inject_decorator(func):
        def decorated(*args, **kwargs):
            args = list(args)
            keys_to_inject = [name for name in injections if name not in kwargs]
            for key in keys_to_inject:
                kwargs[key] = CONTAINER.get(key)
            return func(*args, **kwargs)
        return decorated
    return inject_decorator
