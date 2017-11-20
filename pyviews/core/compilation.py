import ast
from collections import namedtuple
from pyviews.core.ioc import inject
from pyviews.core.observable import Observable

class ExpressionVars(Observable):
    def __init__(self, parent=None):
        super().__init__()
        self._container = parent.to_dictionary() if parent else {}
        self._parent = parent
        if self._parent:
            self._parent.observe_all(self._parent_changed)
        self._own_keys = set()

    def __getitem__(self, key):
        return self._container[key]

    def __setitem__(self, key, value):
        try:
            old_value = self[key]
            self._own_keys.add(key)
        except KeyError:
            old_value = None
        self._set_value(key, value, old_value)

    def _set_value(self, key, value, old_value):
        self._container[key] = value
        self._notify(key, value, old_value)
        self._notify_all(key, value, old_value)

    def _parent_changed(self, key, value, old_value):
        if key in self._own_keys:
            return
        self._set_value(key, value, old_value)

    def to_dictionary(self):
        return self._container.copy()

    def has_key(self, key):
        return key in self._container

    def remove_key(self, key):
        try:
            self._own_keys.discard(key)
            if self._parent and self._parent.has_key(key):
                self._container[key] = self._parent[key]
            else:
                del self._container[key]
        except KeyError:
            pass

class Entry:
    def __init__(self, key):
        self.key = key
        self.entries = None

EXPRESSION_CACHE = {}
class Expression:
    ExpressionItem = namedtuple('ExpressionItem', ['compiled', 'tree'])
    def __init__(self, code):
        self.code = code
        try:
            item = EXPRESSION_CACHE[code]
            self._compiled = item.compiled
            self._var_tree = item.tree
        except KeyError:
            self._compiled = compile(code, '<string>', 'eval')
            self._var_tree = self._compile_var_tree()
            EXPRESSION_CACHE[code] = Expression.ExpressionItem(self._compiled, self._var_tree)

    def _compile_var_tree(self):
        parsed = ast.parse(self.code)
        all_nodes = [node for node in ast.walk(parsed)]

        nodes = [node for node in all_nodes \
                 if isinstance(node, ast.Name)]
        names = {node.id: [] for node in nodes}
        for name in nodes:
            names[name.id].append(name)

        attrs = [node for node in all_nodes \
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
