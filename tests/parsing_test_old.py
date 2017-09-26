from unittest import TestCase, main
from tests.utility import case
import pyviews.common.parsing as tested

class TestParsing(TestCase):
    @case('{namespace}name', ('namespace', 'name'))
    @case('{namespace}{name}', ('namespace', '{name}'))
    @case('{namespace}n}ame', ('namespace', 'n}ame'))
    @case('{namespace}', ('namespace', ''))
    def test_parse_namespace(self, expression, expected):
        self.assertEqual(tested.parse_namespace(expression), expected)

    @case('namespace.name')
    @case('namespace}.name')
    @case('namespace{name}')
    def test_parse_namespace_rases(self, expression):
        with self.assertRaises(tested.ParsingException):
            tested.parse_namespace(expression)

    @case('namespace.name', False)
    @case('namespace}.name', False)
    @case('{namespace.name', False)
    @case('namespace{name}', False)
    @case('namespace{name}', False)
    @case('{namespacename}', True)
    @case('{namespace}name', True)
    @case('{namespace}{name}', True)
    def test_has_namespace(self, expression, has):
        self.assertEqual(tested.has_namespace(expression), has)

if __name__ == '__main__':
    main()
