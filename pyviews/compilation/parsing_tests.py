#pylint: disable=missing-docstring, invalid-name

from unittest import TestCase
from pyviews.testing import case
from .parsing import is_expression, parse_expression

class is_expression_tests(TestCase):
    @case('{asdf}', True)
    @case('once:{asdf}', True)
    @case('oneway:{asdf}', True)
    @case('twoways:{asdf}', True)
    @case('{{asdf}}', True)
    @case('twoways:{{asdf}}', True)
    @case('once:{{asdf}}', True)
    @case('oneway:{{asdf}}', True)
    @case('twoways:{conv:{asdf}}', True)
    @case('twoways:{asdf}', True)
    @case('twoways:{asdf}', True)
    @case('oneway{asdf}', False)
    @case(':{asdf}', False)
    @case('{asdf', False)
    @case('once:{asdf', False)
    @case('asdf}', False)
    @case(' {asdf}', False)
    @case('once: {asdf}', False)
    def test_is_expression(self, expr, expected):
        self.assertEqual(is_expression(expr), expected)

class parse_expression_tests(TestCase):
    @case('{asdf}', ('oneway', 'asdf'))
    @case('once:{asdf}', ('once', 'asdf'))
    @case('oneway:{asdf}', ('oneway', 'asdf'))
    @case('twoways:{asdf}', ('twoways', 'asdf'))
    @case('{{asdf}}', ('twoways', '{asdf}'))
    @case('{to_int:{asdf}}', ('twoways', 'to_int:{asdf}'))
    @case('twoways:{{asdf}}', ('twoways', '{asdf}'))
    @case('oneway:{{asdf}}', ('oneway', '{asdf}'))
    @case('twoways:{to_int:{asdf}}', ('twoways', 'to_int:{asdf}'))
    def test_parse_expression(self, expr, expected):
        self.assertEqual(parse_expression(expr), expected)
