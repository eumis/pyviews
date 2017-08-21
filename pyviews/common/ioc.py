class Container:
    def __init__(self):
        self._initializers = {}

    def register(self, name, initializer):
        if name in self._initializers:
            raise 'Dependency with name ' + name + ' is already exists'
        self._initializers[name] = initializer

    def register_call(self, name, method):
        self.register(name, lambda: method)

    def register_value(self, name, value):
        self.register(name, lambda: value)

    def get(self, name, *args):
        if name not in self._initializers:
            raise 'Dependency with name ' + name + ' is not found'
        return self._initializers[name](*args)

CONTAINER = Container()

def inject(*names):
    def inject_decorator(func):
        def decorated(*args, **kwargs):
            args = list(args)
            keys_to_inject = [name for name in names if name not in kwargs]
            for key in keys_to_inject:
                kwargs[key] = CONTAINER.get(key)
            return func(*args, **kwargs)
        return decorated
    return inject_decorator
