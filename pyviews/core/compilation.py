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
    def __init__(self, message, expression):
        super().__init__(message)
        self.expression = expression
        self.add_info('Expression', expression)

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
            error = CompilationError(syntax_error.text, self.code)
            error.add_cause(syntax_error)
            raise error from syntax_error

    def _build_object_tree(self):
        ast_root = ast.parse(self.code)
        ast_nodes = [node for node in ast.walk(ast_root)]

        is_child = lambda ast_node: isinstance(ast_node, ast.Name)

        root = ObjectNode('root')
        root.children = self._get_children(ast_nodes, is_child)

        return root

    def _get_children(self, ast_nodes, is_child):
        ast_children = [n for n in ast_nodes if is_child(n)]

        grouped = self._group_by_key(ast_children)

        children = []
        for key, key_nodes in grouped.items():
            node = ObjectNode(key)
            is_attribute = lambda n, nds=key_nodes: isinstance(n, ast.Attribute) and n.value in nds
            node.children = self._get_children(ast_nodes, is_attribute)
            children.append(node)

        return children

    def _group_by_key(self, ast_nodes):
        try:
            grouped_by_id = {node.id: [] for node in ast_nodes}
            for ast_child in ast_nodes:
                grouped_by_id[ast_child.id].append(ast_child)
        except AttributeError:
            grouped_by_id = {node.attr: [] for node in ast_nodes}
            for ast_child in ast_nodes:
                grouped_by_id[ast_child.attr].append(ast_child)
        return grouped_by_id

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
            error = CompilationError('Error occured in expression execution', self.code)
            error.add_cause(info[1])
            raise error from info[1]
