from unittest import TestCase, main
from pyviews.testing import case
from pyviews.rendering.expression import is_code_expression, parse_expression

class ExpressionsTests(TestCase):
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
    def test_is_code_expression(self, expr, expected):
        self.assertEqual(is_code_expression(expr), expected)

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

if __name__ == '__main__':
    main()
