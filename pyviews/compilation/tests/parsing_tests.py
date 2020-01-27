from pytest import mark
from pyviews.compilation.parsing import is_expression, parse_expression, ExpressionSource


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
])
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
])
def test_parse_expression(expr: str, expected: ExpressionSource):
    """parse_expression() should return tuple (binding_type, expression body)"""
    assert parse_expression(expr) == expected
