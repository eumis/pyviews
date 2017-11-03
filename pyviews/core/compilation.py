import ast
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
        try:
            old_value = self[key]
        except KeyError:
            old_value = None
        self._container[key] = value
        self._notify(key, value, old_value)

    def own_keys(self):
        return self._container.keys()

    def all_keys(self):
        keys = set(self.own_keys())
        if self._parent is not None:
            keys.update(self._parent.all_keys())
        return keys

    def to_dictionary(self):
        return self._container.copy()

    def to_all_dictionary(self):
        return {key: self[key] for key in self.all_keys()}

    def has_key(self, key):
        return key in self.all_keys()

    def remove_key(self, key):
        try:
            del self._container[key]
        except KeyError:
            pass

class Entry:
    def __init__(self, key):
        self.key = key
        self.entries = None

class Expression:
    def __init__(self, code):
        self.code = code
        self._compiled = compile(code, '<string>', 'eval')
        self._var_tree = self._compile_var_tree()

    def _compile_var_tree(self):
        parsed = ast.parse(self.code)

        nodes = [node for node in ast.walk(parsed) \
                 if isinstance(node, ast.Name)]
        names = {node.id: [] for node in nodes}
        for name in nodes:
            names[name.id].append(name)

        attrs = [node for node in ast.walk(parsed) \
                 if isinstance(node, ast.Attribute)]

        root = Entry('root')
        root.entries = []
        for key, nodes in names.items():
            entry = Entry(key)
            entry.entries = self._get_attr_entires(attrs, nodes)
            root.entries.append(entry)
        return root

    def _get_attr_entires(self, attrs, parents):
        attr_nodes = [attr for attr in attrs if attr.value in parents]

        parent_attrs = {node.attr: [] for node in attr_nodes}
        for node in attr_nodes:
            parent_attrs[node.attr].append(node)
        res = []
        for key, nodes in parent_attrs.items():
            entry = Entry(key)
            entry.entries = self._get_attr_entires(attrs, nodes)
            res.append(entry)
        return res

    def get_var_tree(self):
        return self._var_tree

    def execute(self, parameters=None):
        parameters = {} if parameters is None else parameters
        return eval(self._compiled, parameters, {})
