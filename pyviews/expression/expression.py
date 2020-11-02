"""Expression eval implementation"""

import ast
from collections import namedtuple
from types import CodeType
from typing import List, Callable, Any, Iterator, NamedTuple, Union

from injectool import dependency

from pyviews.core import error_handling
from pyviews.expression.error import ExpressionError

_COMPILATION_CACHE = {}
_CacheItem = namedtuple('CacheItem', ['compiled_code', 'tree'])


class ObjectNode(NamedTuple):
    """Entry of object in expression"""
    key: str
    children: List['ObjectNode']


class Expression:
    """Parses and executes expression."""

    def __init__(self, code):
        self._code: str = code
        self._compiled_code: CodeType
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

    def _compile(self) -> CodeType:
        try:
            code = self._code if self._code.strip(' ') else 'None'
            return compile(code, '<string>', 'eval')
        except SyntaxError as syntax_error:
            error = ExpressionError(syntax_error.msg, self._code)
            error.cause_error = syntax_error
            raise error from syntax_error

    def _build_object_tree(self) -> ObjectNode:
        ast_root = ast.parse(self._code)
        ast_nodes = list(ast.walk(ast_root))
        children = list(self._get_children(ast_nodes, self._is_child))
        return ObjectNode('root', children)

    @staticmethod
    def _is_child(ast_node: ast.AST) -> bool:
        return isinstance(ast_node, ast.Name)

    def _get_children(self, ast_nodes: List[ast.AST], is_child: Callable[[ast.AST], bool]) \
            -> Iterator[ObjectNode]:
        ast_children = [n for n in ast_nodes if is_child(n)]

        grouped = self._group_by_key(ast_children)

        for key, key_nodes in grouped.items():
            children = self._get_children(ast_nodes,
                                          lambda n, nds=key_nodes: self._is_attribute(n, nds))
            yield ObjectNode(key, list(children))

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
    def code(self) -> str:
        """Expression source code"""
        return self._code

    @property
    def compiled_code(self) -> CodeType:
        """Expression compiled code"""
        return self._compiled_code

    def get_object_tree(self) -> ObjectNode:
        """Returns objects tree from expression"""
        return self._object_tree


@dependency
def execute(expression: Union[Expression, str], parameters: dict = None) -> Any:
    """Executes expression with passed parameters and returns result"""
    code = expression.code if isinstance(expression, Expression) else expression
    with error_handling(ExpressionError('Error occurred in expression execution'),
                        lambda e: e.add_expression_info(code)):
        expression = expression if isinstance(expression, Expression) else Expression(expression)
        parameters = {} if parameters is None else parameters
        return eval(expression.compiled_code, parameters, {})
