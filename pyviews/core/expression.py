"""Expression errors"""

import ast
from collections import namedtuple
from re import compile as compile_regex
from types import CodeType
from typing import Any, Dict, Generator, List, NamedTuple, Optional, Union

from injectool import dependency

from pyviews.core.error import PyViewsError, error_handling

_CompiledCode = namedtuple('CacheItem', ['compiled_code', 'tree'])
_COMPILATION_CACHE: Dict[str, _CompiledCode] = {}
_AST_CLASSES = {ast.Name, ast.Attribute, ast.Subscript}

ROOT = 'root'
ENTRY = 'entry'
ATTRIBUTE = 'attribute'
INDEX = 'index'


class ExpressionError(PyViewsError):
    """Error for failed expression"""

    def __init__(self, message: Optional[str] = None, expression_body: Optional[str] = None):
        super().__init__(message = message)
        self.expression: Optional[str] = expression_body
        if expression_body:
            self.add_expression_info(expression_body)

    def add_expression_info(self, expression: str) -> 'ExpressionError':
        """Adds info about expression to error"""
        self.expression = expression
        self.add_info('Expression', expression)
        return self

    def _get_error(self) -> Generator[str, None, None]:
        yield from super()._get_error()
        yield self._format_info('Expression', self.expression if self.expression else '')


def _get_index_value(ast_node: ast.Subscript) -> Any:
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


class ObjectNode(NamedTuple):
    """Root entry in expression"""
    key: str
    type: str
    children: List['ObjectNode']


def _level_key(ast_node: ast.AST):
    level = 0
    while hasattr(ast_node, 'value'):
        level = level + 1
        ast_node = ast_node.value
    return level


class Expression:
    """Parses and executes expression."""

    __slots__ = ('_code', '_compiled_code', '_object_tree')

    def __init__(self, code):
        self._code: str = code
        self._compiled_code: CodeType
        self._object_tree: ObjectNode
        if not self._init_from_cache():
            self._compiled_code = self._compile(code)
            self._object_tree = self._build_object_tree(code)
            self._store_to_cache()

    def _init_from_cache(self) -> bool:
        compiled = _COMPILATION_CACHE.get(self._code)
        if compiled is None:
            return False
        self._compiled_code = compiled.compiled_code
        self._object_tree = compiled.tree
        return True

    @staticmethod
    def _compile(code: str) -> CodeType:
        try:
            code = code if code.strip(' ') else 'None'
            return compile(code, '<string>', 'eval')
        except SyntaxError as syntax_error:
            error = ExpressionError(syntax_error.msg, code)
            error.cause_error = syntax_error
            raise error from syntax_error

    @staticmethod
    def _build_object_tree(code: str) -> ObjectNode:
        root = ObjectNode('root', ROOT, [])
        ast_root = ast.parse(code)
        nodes: Dict[ast.AST, ObjectNode] = {}
        ast_nodes = sorted((item for item in ast.walk(ast_root) if item.__class__ in _AST_CLASSES), key = _level_key)
        for ast_node in ast_nodes:
            if isinstance(ast_node, ast.Name):
                try:
                    node = next(n for n in root.children if n.key == ast_node.id)
                except StopIteration:
                    node = ObjectNode(ast_node.id, ENTRY, [])
                    root.children.append(node)
                nodes[ast_node] = node
            if isinstance(ast_node, ast.Attribute):
                ast_parent = ast_node.value
                try:
                    node = next(n for n in nodes[ast_parent].children if n.key == ast_node.attr)
                except StopIteration:
                    node = ObjectNode(ast_node.attr, ATTRIBUTE, [])
                    nodes[ast_parent].children.append(node)
                nodes[ast_node] = node
            if isinstance(ast_node, ast.Subscript):
                ast_parent = ast_node.value
                key = _get_index_value(ast_node)
                try:
                    node = next(n for n in nodes[ast_parent].children if n.key == key)
                except StopIteration:
                    node = ObjectNode(key, INDEX, [])
                    nodes[ast_parent].children.append(node)
                nodes[ast_node] = node
        return root

    def _store_to_cache(self):
        item = _CompiledCode(self._compiled_code, self._object_tree)
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
def execute(expression: Union[Expression, str], parameters: Optional[dict] = None) -> Any:
    """Executes expression with passed parameters and returns result"""
    code = expression.code if isinstance(expression, Expression) else expression
    with error_handling(ExpressionError('Error occurred in expression execution', code)):
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
