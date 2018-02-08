import ast
from sys import exc_info
from collections import namedtuple
from pyviews.core import CoreError
from pyviews.core.observable import InheritedDict

class Entry:
    def __init__(self, key):
        self.key = key
        self.entries = None

class ExpressionError(CoreError):
    pass

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
            try:
                self._compiled = compile(code, '<string>', 'eval')
                self._var_tree = self._compile_var_tree()
                EXPRESSION_CACHE[code] = Expression.ExpressionItem(self._compiled, self._var_tree)
            except SyntaxError as syntax_error:
                raise ExpressionError('Expression "{' + code + '"} compilation is failed', syntax_error.msg) \
                      from syntax_error

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
        try:
            parameters = {} if parameters is None else parameters
            return eval(self._compiled, parameters, {})
        except:
            info = exc_info()
            raise ExpressionError('Error occured in execution of "' + self.code + '"', str(info[1])) \
                  from info[1]
