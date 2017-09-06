class Container:
    def __init__(self):
        self._initializers = {}

    def register(self, name, initializer: callable, param=None):
        if not callable(initializer):
            raise ValueError('Initializer should be callable', initializer)
        if name not in self._initializers:
            self._initializers[name] = {}
        self._initializers[name][param] = initializer

    def get(self, name, param=None):
        if name not in self._initializers:
            raise ValueError('Dependency with name ' + name + ' is not found')
        param = param if param in self._initializers[name] else None
        return self._initializers[name][param]()

CONTAINER = Container()

def register(name, initializer: callable, param=None):
    CONTAINER.register(name, initializer, param)

def register_value(name, value, param=None):
    CONTAINER.register(name, lambda: value, param)

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
