"""Expression errors"""

import ast
from collections import namedtuple
from functools import partial
from re import compile as compile_regex
from types import CodeType
from typing import Any, Callable, Dict, Generator, List, NamedTuple, Optional, Set, Tuple, Union

from injectool import dependency

from pyviews.core.error import PyViewsError, error_handling

_COMPILATION_CACHE = {}
_CacheItem = namedtuple('CacheItem', ['compiled_code', 'tree'])
_AST_CLASSES = {ast.Name, ast.Attribute, ast.Subscript}

ROOT = 'root'
ENTRY = 'entry'
ATTRIBUTE = 'attribute'
INDEX = 'index'

_TYPES = {ast.Name: ENTRY, ast.Attribute: ATTRIBUTE, ast.Subscript: INDEX}


class ExpressionError(PyViewsError):
    """Error for failed expression"""

    def __init__(self, message: Optional[str] = None, expression_body: Optional[str] = None):
        super().__init__(message = message)
        self.expression: Optional[str] = expression_body
        if expression_body:
            self.add_expression_info(expression_body)

    def add_expression_info(self, expression: str):
        """Adds info about expression to error"""
        self.expression = expression
        self.add_info('Expression', expression)

    def _get_error(self) -> Generator[str, None, None]:
        yield from super()._get_error()
        yield self._format_info('Expression', self.expression if self.expression else '')


def _get_index_value(ast_node: ast.Subscript):
    ast_node = ast_node.slice.value if isinstance(ast_node.slice, ast.Index) else ast_node.slice
    if isinstance(ast_node, ast.Constant):
        return ast_node.value
    if isinstance(ast_node, ast.Num):
        return ast_node.n
    return _get_attr_expression(ast_node)


def _get_attr_expression(ast_node: Union[ast.Name, ast.Attribute, ast.Subscript]) -> 'Expression':
    result = ''
    while isinstance(ast_node, ast.Attribute):
        result = f'.{ast_node.attr}{result}'
        ast_node = ast_node.value
    return Expression(f'{ast_node.id}{result}')


_KEYS = {ast.Name: lambda n: n.id, ast.Attribute: lambda n: n.attr, ast.Subscript: _get_index_value}


class ObjectNode(NamedTuple):
    """Root entry in expression"""
    key: str
    type: str
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
        ast_nodes = {n for n in ast.walk(ast_root) if n.__class__ in _AST_CLASSES}
        return ObjectNode('root', ROOT, self._create_nodes(ast_nodes, self._is_name))

    @staticmethod
    def _is_name(ast_node: ast.AST) -> bool:
        return isinstance(ast_node, ast.Name)

    def _create_nodes(self, ast_nodes: Set[ast.AST], node_filter: Callable[[ast.AST], bool]) \
            -> List[ObjectNode]:
        ast_nodes_to_create = {n for n in ast_nodes if node_filter(n)}
        ast_nodes = ast_nodes.difference(ast_nodes_to_create)

        grouped = self._group(ast_nodes_to_create).items()
        return [
            ObjectNode(key, node_type, self._create_nodes(ast_nodes, partial(self._is_child, nodes)))
            for key, (nodes, node_type) in grouped
        ]

    @staticmethod
    def _is_child(key_nodes: set, ast_node: ast.AST) -> bool:
        return ast_node.value in key_nodes

    @staticmethod
    def _group(ast_nodes: Set[ast.AST]) -> Dict[str, Tuple[Set[ast.AST], str]]:
        result = {}
        for ast_node in ast_nodes:
            key = _KEYS[ast_node.__class__](ast_node)
            if key not in result:
                result[key] = ({ast_node}, _TYPES[ast_node.__class__])
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
    with error_handling(
        ExpressionError('Error occurred in expression execution'), lambda e: e.add_expression_info(code)
    ):
        expression = expression if isinstance(expression, Expression) else Expression(expression)
        parameters = {} if parameters is None else parameters
        return eval(expression.compiled_code, parameters, {})


EXPRESSION_REGEX = compile_regex(r'([a-zA-Z_]{1,}\:){0,1}\{.*\}')


def is_expression(source: str) -> bool:
    """Return true if passed value is expression"""
    return EXPRESSION_REGEX.fullmatch(source) is not None


ParsedExpression = namedtuple('Expression', ['binding_type', 'body'])


def parse_expression(source: str) -> ParsedExpression:
    """Returns tuple with expression type and expression body"""
    if not is_expression(source):
        raise ExpressionError('Expression is not valid', source)
    if not source.startswith('{'):
        binding_type, source = source.split(':', 1)
    elif source.startswith('{{') and source.endswith('}}'):
        binding_type, source = 'twoways', source[1:-1]
    else:
        binding_type = 'oneway'
    return ParsedExpression(binding_type, source[1:-1])
