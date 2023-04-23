from pytest import mark, raises

from pyviews.core.expression import (Expression, ExpressionError, ParsedExpression, execute, is_expression,
                                     parse_expression)

_EXPRESSION_TEST_PARAMETERS = [
    ('', None, None),
    (' ', {'some_key': 1}, None),
    ('2 + 2', None, 4),
    ('some_key', {'some_key': 1}, 1),
    ('some_key - 1', {'some_key': 1}, 0),
    ('str(some_key)', {'some_key': 1}, '1'),
    ('some_key', {'some_key': 'asdf'}, 'asdf'),
    ('some_key(some_value)', {'some_key': lambda val: val, 'some_value': 'value'}, 'value')
] # yapf: disable


class ExecuteTests:

    @staticmethod
    @mark.parametrize('code, params, expected', _EXPRESSION_TEST_PARAMETERS)
    def test_execute_expression(code, params, expected):
        """execute() should return expression value"""
        expression = Expression(code)

        actual = execute(expression, params)

        assert expected == actual

    @staticmethod
    @mark.parametrize('code, params, expected', _EXPRESSION_TEST_PARAMETERS)
    def test_execute_source_code(code, params, expected):
        """execute() should return expression value"""
        actual = execute(code, params)

        assert expected == actual

    @staticmethod
    @mark.parametrize('expression', ['2/0', Expression('print(some_variable)')])
    def test_execute_scope(expression):
        """execute() should keep scope for lambdas"""
        expression = 'lambda: key'
        node_globals = {'key': 2}
        func = execute(expression, node_globals)

        actual = func()

        assert actual == 2

    @staticmethod
    @mark.parametrize('expression', ['2/0', Expression('print(some_variable)')])
    def test_execute_raises(expression):
        """execute() should raise error if expression is invalid"""
        with raises(ExpressionError):
            execute(expression)


@mark.parametrize('expr, expected', [
    ('{asdf}', True),
    ('once:{asdf}', True),
    ('oneway:{asdf}', True),
    ('twoways:{asdf}', True),
    ('{{asdf}}', True),
    ('twoways:{{asdf}}', True),
    ('once:{{asdf}}', True),
    ('oneway:{{asdf}}', True),
    ('twoways:{conv:{asdf}}', True),
    ('twoways:{asdf}', True),
    ('twoways:{asdf}', True),
    ('bind:{asdf}:{qwerty}', True),
    ('oneway{asdf}', False),
    (':{asdf}', False),
    ('{asdf', False),
    ('once:{asdf', False),
    ('asdf}', False),
    (' {asdf}', False),
    ('once: {asdf}', False),
]) # yapf: disable
def test_is_expression(expr: str, expected: bool):
    """is_expression() should return True for valid expression by syntax"""
    assert is_expression(expr) == expected


@mark.parametrize('expr, expected', [
    ('{asdf}', ('oneway', 'asdf')),
    ('once:{asdf}', ('once', 'asdf')),
    ('oneway:{asdf}', ('oneway', 'asdf')),
    ('twoways:{asdf}', ('twoways', 'asdf')),
    ('{{asdf}}', ('twoways', 'asdf')),
    ('{to_int:{asdf}}', ('oneway', 'to_int:{asdf}')),
    ('binding:{to_int:{asdf}}', ('binding', 'to_int:{asdf}')),
    ('twoways:{{asdf}}', ('twoways', '{asdf}')),
    ('oneway:{{asdf}}', ('oneway', '{asdf}')),
    ('twoways:{to_int:{asdf}}', ('twoways', 'to_int:{asdf}')),
    ('bind:{qwer}:{asdf}', ('bind', 'qwer}:{asdf')),
]) # yapf: disable
def test_parse_expression(expr: str, expected: ParsedExpression):
    """parse_expression() should return tuple (binding_type, expression body)"""
    assert parse_expression(expr) == expected
