class Container:
    def __init__(self):
        self._initializers = {}

    def register(self, name, initializer):
        self._initializers[name] = initializer

    def get(self, name, *args):
        if name not in self._initializers:
            raise 'Dependency with name ' + name + ' is not found'
        return self._initializers[name](*args)

CONTAINER = Container()

def register(name, initializer):
    CONTAINER.register(name, initializer)

def register_call(name, method):
    CONTAINER.register(name, lambda: method)

def register_value(name, value):
    CONTAINER.register(name, lambda: value)

def get(name, *args):
    return CONTAINER.get(name, *args)

def inject(*names):
    def inject_decorator(func):
        def decorated(*args, **kwargs):
            args = list(args)
            keys_to_inject = [name for name in names if name not in kwargs]
            for key in keys_to_inject:
                kwargs[key] = get(key)
            return func(*args, **kwargs)
        return decorated
    return inject_decorator
