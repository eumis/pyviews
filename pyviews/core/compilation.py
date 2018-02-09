'''Module to parse and compile python expressions'''

import ast
from sys import exc_info
from collections import namedtuple
from pyviews.core import CoreError

class ObjectNode:
    '''Entry of object in expression'''
    def __init__(self, key):
        self.key = key
        self.children = []

class CompilationError(CoreError):
    '''Error for failed expression compilation'''
    CompileFailed = 'Expression "{0}" compilation is failed.'
    ExecutionFailed = 'Error occured in execution of "{0}"'

class Expression:
    '''Parses and executes expression.'''
    EXPRESSION_CACHE = {}
    CacheItem = namedtuple('ExpressionItem', ['compiled_code', 'tree'])
    def __init__(self, code):
        self.code = code
        self._compiled_code = None
        self._object_tree = None
        if not self._init_from_cache():
            self._compiled_code = self._compile()
            self._object_tree = self._build_object_tree()
            self._store_to_cache()

    def _init_from_cache(self):
        try:
            item = Expression.EXPRESSION_CACHE[self.code]
            self._compiled_code = item.compiled_code
            self._object_tree = item.tree
        except KeyError:
            return False
        return True

    def _compile(self):
        try:
            return compile(self.code, '<string>', 'eval')
        except SyntaxError as syntax_error:
            msg = CompilationError.CompileFailed.format(self.code)
            raise CompilationError(msg, syntax_error.msg) from syntax_error

    def _build_object_tree(self):
        ast_root = ast.parse(self.code)
        ast_nodes = [node for node in ast.walk(ast_root)]

        return self._create_object_nodes(ast_nodes)

    def _create_object_nodes(self, ast_nodes):
        names_map = self._get_names_map(ast_nodes)

        ast_attrs = [node for node in ast_nodes \
                 if isinstance(node, ast.Attribute)]

        root = ObjectNode('root')
        for key, nodes in names_map.items():
            entry = ObjectNode(key)
            entry.children = self._get_attr_nodes(ast_attrs, nodes)
            root.children.append(entry)
        return root

    def _get_names_map(self, ast_nodes):
        ast_names = [node for node in ast_nodes \
                 if isinstance(node, ast.Name)]
        names_map = {node.id: [] for node in ast_names}

        for name in ast_names:
            names_map[name.id].append(name)

        return names_map

    def _get_attr_nodes(self, ast_attrs, parents):
        attr_nodes = [attr for attr in ast_attrs if attr.value in parents]

        parent_attrs = {node.attr: [] for node in attr_nodes}
        for node in attr_nodes:
            parent_attrs[node.attr].append(node)
        res = []
        for key, nodes in parent_attrs.items():
            entry = ObjectNode(key)
            entry.children = self._get_attr_nodes(ast_attrs, nodes)
            res.append(entry)
        return res

    def _store_to_cache(self):
        item = Expression.CacheItem(self._compiled_code, self._object_tree)
        Expression.EXPRESSION_CACHE[self.code] = item

    def get_object_tree(self):
        '''Returns objects tree from expression'''
        return self._object_tree

    def execute(self, parameters: dict = None):
        '''Executes expression with passed parameters and returns result'''
        try:
            parameters = {} if parameters is None else parameters
            return eval(self._compiled_code, parameters, {})
        except:
            info = exc_info()
            msg = CompilationError.ExecutionFailed.format(self.code)
            raise CompilationError(msg, str(info[1])) from info[1]
