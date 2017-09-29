from pyviews.core.observable import Observable

class ExpressionVars(Observable):
    def __init__(self, parent=None):
        super().__init__()
        self._container = {}
        self._parent = parent

    def __getitem__(self, key):
        if key in self._container:
            return self._container[key]
        if self._parent is not None:
            return self._parent[key]
        raise KeyError(key)

    def __setitem__(self, key, value):
        old_value = self[key]
        self._container[key] = value
        self._notify(key, value, old_value)

    def own_keys(self):
        return self._container.keys()

    def all_keys(self):
        keys = set(self.own_keys())
        if self._parent is not None:
            keys.update(self._parent.own_keys())
        return keys

    def to_dictionary(self):
        return self._container.copy()

    def to_all_dictionary(self):
        return {key: self[key] for key in self.all_keys()}

class Expression:
    def __init__(self, code, parameters=None):
        self.code = code
        self._parameters = {} if parameters is None else parameters

    def get_parameters(self):
        return self._parameters.copy()

    def compile(self, parameters=None):
        params = self.get_parameters()
        if parameters is not None:
            params.update(parameters)
        return eval(self.code, params, {})
