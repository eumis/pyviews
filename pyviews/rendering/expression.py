'''Parsing methods'''

from re import compile as compile_regex

EXPRESSION_REGEX = compile_regex(r'([a-zA-Z_]{1,}\:){0,1}\{.*\}')
def is_code_expression(expression):
    '''Return true if passed value is binding expression'''
    return EXPRESSION_REGEX.fullmatch(expression) != None

def parse_expression(expression):
    '''Returns tuple with binding type and expression body'''
    if expression[0] != '{':
        [binding_type, expression] = expression.split(':', 1)
    elif expression.endswith('}}'):
        binding_type = 'twoways'
    else:
        binding_type = 'oneway'
    return (binding_type, expression[1:-1])
