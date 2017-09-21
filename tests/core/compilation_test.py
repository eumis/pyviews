from unittest import TestCase, main
from tests.utility import case
from pyviews.core.compilation import Expression

class TestExpression(TestCase):
    @case('2 + 2', None, 4)
    @case('some_key', {'some_key': 1}, 1)
    @case('some_key - 1', {'some_key': 1}, 0)
    @case('str(some_key)', {'some_key': 1}, '1')
    @case('some_key', {'some_key': 'asdf'}, 'asdf')
    @case('some_key(some_value)', {'some_key': lambda val: val, 'some_value': 'value'}, 'value')
    def test_compile_result(self, code, params, expected):
        expression = Expression(code, params)
        msg = 'compile should return expression result value'
        self.assertEqual(expression.compile(), expected, msg)

    @case('(one, two)', {'one': 1}, {'two': 'two value'}, (1, 'two value'))
    @case('(one, two)', {'one': 1}, {'one': 'one value', 'two': 'two value'}, ('one value', 'two value'))
    @case('(one, two)', None, {'one': 'one value', 'two': 'two value'}, ('one value', 'two value'))
    def test_compile_parameters(self, code, params, compile_params, expected):
        expression = Expression(code, params)
        msg = 'compile should merge parameters passed to method'
        self.assertEqual(expression.compile(compile_params), expected, msg)

    def test_get_parameters(self):
        expression = Expression('some_key', {'some_key': 'param value'})
        expression.get_parameters()['some_key'] = 'updated value'
        msg = 'get_parameters should return copy of parameters'
        self.assertEqual(expression.compile(), 'param value', msg)

if __name__ == '__main__':
    main()
