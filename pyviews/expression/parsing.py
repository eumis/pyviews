"""Expression parsing methods"""

from re import compile as compile_regex
from collections import namedtuple

from pyviews.expression.error import ExpressionError

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
