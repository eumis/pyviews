"""Expression parsing methods"""

from re import compile as compile_regex
from collections import namedtuple
from pyviews.core import CoreError


class ExpressionError(CoreError):
    """Error for expression"""

    def __init__(self, message, expression):
        super().__init__(message)
        self.add_info('Expression', expression)


EXPRESSION_REGEX = compile_regex(r'([a-zA-Z_]{1,}\:){0,1}\{.*\}')
ExpressionSource = namedtuple('Expression', ['type', 'code'])


def is_expression(source: str) -> bool:
    """Return true if passed value is expression"""
    return EXPRESSION_REGEX.fullmatch(source) is not None


def parse_expression(source: str) -> ExpressionSource:
    """Returns tuple with expression type and expression body"""
    if not is_expression(source):
        msg = 'Expression is not valid. Expression should be matched with regular expression: {0}' \
            .format(EXPRESSION_REGEX)
        raise ExpressionError(msg, source)
    if not source.startswith('{'):
        [type_, source] = source.split(':', 1)
    elif source.endswith('}}'):
        type_ = 'twoways'
    else:
        type_ = 'oneway'
    return ExpressionSource(type_, source[1:-1])
