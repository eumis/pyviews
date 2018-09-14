'''Parsing methods'''

from re import compile as compile_regex
from typing import Tuple
from pyviews.core import CoreError

class ExpressionError(CoreError):
    '''Error for expression'''
    def __init__(self, message, expression):
        super().__init__(message)
        self.add_info('Expression', expression)

EXPRESSION_REGEX = compile_regex(r'([a-zA-Z_]{1,}\:){0,1}\{.*\}')

def is_code_expression(expression):
    '''Return true if passed value is binding expression'''
    return EXPRESSION_REGEX.fullmatch(expression) != None

def parse_expression(expression: str) -> Tuple[str, str]:
    '''Returns tuple with binding type and expression body'''
    if not is_code_expression(expression):
        msg = 'Expression is not valid. Expression should be matched with regular expression: {0}'\
              .format(EXPRESSION_REGEX)
        raise ExpressionError(msg, expression)
    if expression[0] != '{':
        [binding_type, expression] = expression.split(':', 1)
    elif expression.endswith('}}'):
        binding_type = 'twoways'
    else:
        binding_type = 'oneway'
    return (binding_type, expression[1:-1])
