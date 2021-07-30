"""Expression eval implementation"""

import ast
from collections import namedtuple
from functools import partial
from types import CodeType
from typing import List, Callable, Any, NamedTuple, Union, Set, Dict, Tuple

from injectool import dependency

from pyviews.core import error_handling
from pyviews.expression.error import ExpressionError

_COMPILATION_CACHE = {}
_CacheItem = namedtuple('CacheItem', ['compiled_code', 'tree'])
_AST_CLASSES = {ast.Name, ast.Attribute, ast.Subscript}
_KEYS = {
    ast.Name: lambda n: n.id,
    ast.Attribute: lambda n: n.attr,
    ast.Subscript: lambda n: n.slice.value.value
}
GetValue = Callable[[Any, Any], None]
_GET_VALUE = {
    ast.Name: lambda node, inst: inst.get(node.key),
    ast.Attribute: lambda node, inst: getattr(inst, node.key),
    ast.Subscript: lambda node, inst: inst[node.key]
}


class ObjectNode(NamedTuple):
    """Entry of object in expression"""
    key: str
    children: List['ObjectNode']
    get_value: GetValue


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
        ast_nodes = {n for n in ast.walk(ast_root) if n.__class__ in _AST_CLASSES}
        return ObjectNode('root', list(self._create_nodes(ast_nodes, self._is_name)),
                          _GET_VALUE[ast.Subscript])

    @staticmethod
    def _is_name(ast_node: ast.AST) -> bool:
        return isinstance(ast_node, ast.Name)

    def _create_nodes(self, ast_nodes: Set[ast.AST], selected: Callable[[ast.AST], bool]) \
            -> List[ObjectNode]:
        selected_ast_nodes = {n for n in ast_nodes if selected(n)}
        ast_nodes = ast_nodes.difference(selected_ast_nodes)

        grouped = self._group_duplicates(selected_ast_nodes).items()
        return [ObjectNode(key, self._create_nodes(ast_nodes, partial(self._is_child, nodes[0])),
                           nodes[1])
                for key, nodes in grouped]

    @staticmethod
    def _is_child(key_nodes: set, ast_node: ast.AST) -> bool:
        return not isinstance(ast_node, ast.Name) and ast_node.value in key_nodes

    @staticmethod
    def _group_duplicates(ast_nodes: Set[ast.AST]) -> Dict[str, Tuple[Set[ast.AST], GetValue]]:
        result = {}
        for ast_node in ast_nodes:
            key = _KEYS[ast_node.__class__](ast_node)
            if key not in result:
                result[key] = ({ast_node}, _GET_VALUE[ast_node.__class__])
            else:
                result[key][0].add(ast_node)
        return result

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
