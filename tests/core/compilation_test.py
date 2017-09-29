from unittest import TestCase, main
from tests.utility import case
from pyviews.core.compilation import Expression, ExpressionVars

class TestGlobals(TestCase):
    def test_globals_keys(self):
        parent = ExpressionVars()
        parent['one'] = 1
        parent['two'] = 2

        globs = ExpressionVars(parent)
        globs['two'] = 'two'
        globs['three'] = 'three'

        self.assertEqual(globs['one'], 1, 'Globals should get values from parent')
        msg = 'Globals should get own value if key exists'
        self.assertEqual(globs['two'], 'two', msg)
        self.assertEqual(globs['three'], 'three', msg)

    def test_parent_keys(self):
        parent = ExpressionVars()
        parent['one'] = 1
        parent['two'] = 2

        globs = ExpressionVars(parent)
        globs['two'] = 'two'
        globs['three'] = 'three'

        msg = 'own_keys should return only own keys'
        self.assertEqual(sorted(globs.own_keys()), sorted(['two', 'three']), msg)

        msg = 'all_keys should return own keys plus parent keys'
        self.assertEqual(sorted(globs.all_keys()), sorted(['one', 'two', 'three']), msg)

    def test_dictionary(self):
        parent = ExpressionVars()
        parent['one'] = 1
        parent['two'] = 2

        globs = ExpressionVars(parent)
        globs['two'] = 'two'
        globs['three'] = 'three'

        msg = 'to_dictionary should return dictionary with own keys'
        self.assertEqual(globs.to_dictionary(), {'two': 'two', 'three': 'three'}, msg)

        msg = 'to_all_dictionary should return dictionary with all keys'
        self.assertEqual(globs.to_all_dictionary(), {'one': 1, 'two': 'two', 'three': 'three'}, msg)

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
