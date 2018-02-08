'''Module to parse and compile python expressions'''

import ast
from sys import exc_info
from collections import namedtuple
from pyviews.core import CoreError

class Entry:
    '''Node of expression tree built by Expression class'''
    def __init__(self, key):
        self.key = key
        self.entries = None

class CompilationError(CoreError):
    '''Error for failed expression compilation'''
    CompileFailed = 'Expression "{0}" compilation is failed.'
    ExecutionFailed = 'Error occured in execution of "{0}"'

EXPRESSION_CACHE = {}

class Expression:
    '''Builds tree for expression. Execute expression.'''
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
                self._var_tree = self._build_tree()
                EXPRESSION_CACHE[code] = Expression.ExpressionItem(self._compiled, self._var_tree)
            except SyntaxError as syntax_error:
                msg = CompilationError.CompileFailed.format(code)
                raise CompilationError(msg, syntax_error.msg) from syntax_error

    def _build_tree(self):
        ast_node = ast.parse(self.code)
        all_nodes = [node for node in ast.walk(ast_node)]
        nodes = [node for node in all_nodes \
                 if isinstance(node, ast.Name)]
        names = {node.id: [] for node in nodes}

        for name in nodes:
            names[name.id].append(name)

        attrs = [node for node in all_nodes \
                 if isinstance(node, ast.Attribute)]

        return self._create_nodes(names, attrs)

    def _create_nodes(self, names, attrs):
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

    def get_tree(self):
        '''Returns expression tree'''
        return self._var_tree

    def execute(self, parameters: dict = None):
        '''Executes expression with passed parameters and returns result'''
        try:
            parameters = {} if parameters is None else parameters
            return eval(self._compiled, parameters, {})
        except:
            info = exc_info()
            msg = CompilationError.ExecutionFailed.format(self.code)
            raise CompilationError(msg, str(info[1])) from info[1]
