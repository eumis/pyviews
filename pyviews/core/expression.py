"""Expression errors"""

from collections import namedtuple
from re import compile as compile_regex
from types import CodeType
from typing import Any, Dict, Generator, Optional, Union

from injectool import dependency

from pyviews.core.error import PyViewsError, error_handling

_COMPILATION_CACHE: Dict[str, CodeType] = {}


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


class Expression:
    """Parses and executes expression."""

    __slots__ = ('_code', '_compiled_code')

    def __init__(self, code: str, compile_mode: str = 'eval'):
        self._code: str = code
        self._compiled_code: CodeType
        if not self._init_from_cache():
            self._compiled_code = self._compile(code, compile_mode)
            self._store_to_cache()

    def _init_from_cache(self) -> bool:
        compiled = _COMPILATION_CACHE.get(self._code)
        if compiled is None:
            return False
        self._compiled_code = compiled
        return True

    @staticmethod
    def _compile(code: str, compile_mode: str) -> CodeType:
        try:
            code = code if code.strip(' ') else 'None'
            return compile(code, '<string>', compile_mode)
        except SyntaxError as syntax_error:
            error = ExpressionError(syntax_error.msg, code)
            error.cause_error = syntax_error
            raise error from syntax_error

    def _store_to_cache(self):
        _COMPILATION_CACHE[self._code] = self._compiled_code

    @property
    def code(self) -> str:
        """Expression source code"""
        return self._code

    @property
    def compiled_code(self) -> CodeType:
        """Expression compiled code"""
        return self._compiled_code


@dependency
def execute(expression: Union[Expression, str], parameters: Optional[dict] = None) -> Any:
    """Executes expression with passed parameters and returns result"""
    code = expression.code if isinstance(expression, Expression) else expression
    with error_handling(ExpressionError('Error occurred in expression execution', code)):
        expression = expression if isinstance(expression, Expression) else Expression(expression)
        parameters = {} if parameters is None else parameters
        return eval(expression.compiled_code, {}, parameters)


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
