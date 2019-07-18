"""Expression eval implementation"""

import ast
from sys import exc_info
from typing import List, Callable, Any
from collections import namedtuple
from pyviews.core import Expression, ObjectNode, CompilationError

_COMPILATION_CACHE = {}
_CacheItem = namedtuple('CacheItem', ['compiled_code', 'tree'])


class CompiledExpression(Expression):
    """Parses and executes expression."""

    def __init__(self, code):
        super().__init__(code)
        self._compiled_code: ast.AST
        self._object_tree: ObjectNode
        if not self._init_from_cache():
            self._compiled_code = self._compile()
            self._object_tree = self._build_object_tree()
            self._store_to_cache()

    def _init_from_cache(self) -> bool:
        try:
            item = _COMPILATION_CACHE[self._code]
            self._compiled_code = item.compiled_code
            self._object_tree = item.tree
        except KeyError:
            return False
        return True

    def _compile(self) -> ast.AST:
        try:
            code = self._code if self._code.strip(' ') else 'None'
            return compile(code, '<string>', 'eval')
        except SyntaxError as syntax_error:
            error = CompilationError(syntax_error.msg, self._code)
            error.add_cause(syntax_error)
            raise error from syntax_error

    def _build_object_tree(self) -> ObjectNode:
        ast_root = ast.parse(self._code)
        ast_nodes = [node for node in ast.walk(ast_root)]

        root = ObjectNode('root')
        root.children = self._get_children(ast_nodes, self._is_child)

        return root

    @staticmethod
    def _is_child(ast_node: ast.AST) -> bool:
        return isinstance(ast_node, ast.Name)

    def _get_children(self, ast_nodes: List[ast.AST], is_child: Callable[[ast.AST], bool]) -> List[ObjectNode]:
        ast_children = [n for n in ast_nodes if is_child(n)]

        grouped = self._group_by_key(ast_children)

        children = []
        for key, key_nodes in grouped.items():
            node = ObjectNode(key)
            node.children = self._get_children(ast_nodes, lambda n, nds=key_nodes: self._is_attribute(n, nds))
            children.append(node)

        return children

    @staticmethod
    def _is_attribute(ast_node: ast.AST, key_nodes: dict) -> bool:
        return isinstance(ast_node, ast.Attribute) and ast_node.value in key_nodes

    @staticmethod
    def _group_by_key(ast_nodes) -> dict:
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
        item = _CacheItem(self._compiled_code, self._object_tree)
        _COMPILATION_CACHE[self._code] = item

    @property
    def get_object_tree(self) -> ObjectNode:
        """Returns objects tree from expression"""
        return self._object_tree

    def execute(self, parameters: dict = None) -> Any:
        """Executes expression with passed parameters and returns result"""
        try:
            parameters = {} if parameters is None else parameters
            return eval(self._compiled_code, parameters, {})
        except:
            info = exc_info()
            error = CompilationError('Error occurred in expression execution', self.code)
            error.add_cause(info[1])
            raise error from info[1]
