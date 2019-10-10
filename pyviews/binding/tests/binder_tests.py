from unittest.mock import Mock, call

from pytest import mark, raises, fixture

from pyviews.core import BindingError, Node, XmlAttr, Binding
from pyviews.binding.binder import Binder, BindingContext, BindingRule

BINDING_TYPE = 'default_binding_type'


@fixture
def binding_context_fixture(request):
    request.cls.context = BindingContext()


@mark.usefixtures('binding_context_fixture')
class BindingContextTests:
    """BindingContext tests"""

    def test_node(self):
        """node property should use key 'node'"""
        value = Node(Mock())
        init_value = self.context.node

        self.context.node = value

        assert init_value is None
        assert self.context.node == value
        assert self.context['node'] == value

    def test_expression_body(self):
        """expression_body property should use key 'expression_body'"""
        value = "1 + 1"
        init_value = self.context.expression_body

        self.context.expression_body = value

        assert init_value is None
        assert self.context.expression_body == value
        assert self.context['expression_body'] == value

    def test_modifier(self):
        """modifier property should use key 'modifier'"""

        def value(_, __, ___):
            pass

        init_value = self.context.modifier

        self.context.modifier = value

        assert init_value is None
        assert self.context.modifier == value
        assert self.context['modifier'] == value

    def test_xml_attr(self):
        """xml_attr property should use key 'xml_attr'"""
        value = XmlAttr('name')
        init_value = self.context.xml_attr

        self.context.xml_attr = value

        assert init_value is None
        assert self.context.xml_attr == value
        assert self.context['xml_attr'] == value


class TestRule(BindingRule):
    def __init__(self, suitable: bool, binding: Binding = None):
        self._suitable = suitable
        self.suitable_args = None
        self.apply_args = None
        self.binding = binding

    def suitable(self, context: BindingContext):
        self.suitable_args = context
        return self._suitable

    def apply(self, context: BindingContext):
        self.apply_args = context
        return self.binding


def _find_suitable_rule(rules):
    try:
        expected = next(rule for rule in reversed(rules) if rule.suitable())
    except StopIteration:
        expected = None
    return expected


def _create_binder(binding_type, rules):
    binder = Binder()
    for rule in rules:
        binder.add_rule(binding_type, rule)
    return binder


_binding_args = [
    {},
    {'node': Mock()},
    {'node': Mock(), 'modifier': lambda *args: None}
]


class BinderTests:
    @staticmethod
    @mark.parametrize('rules, rule_index', [
        [[TestRule(True), TestRule(True)], 1],
        [[TestRule(False), TestRule(True)], 1],
        [[TestRule(True), TestRule(False)], 0],
        [[TestRule(False), TestRule(False)], None]
    ])
    def test_returns_suitable_rule(rules, rule_index):
        """find_rule() should return first suitable rule by LIFO"""
        binder = _create_binder(BINDING_TYPE, rules)
        expected = rules[rule_index] if rule_index is not None else None

        actual = binder.find_rule(BINDING_TYPE, BindingContext())

        assert expected == actual

    @staticmethod
    def test_returns_rule_by_type():
        """find_rule() should return suitable rule for provided type"""
        binder = _create_binder('one_type', [TestRule(True)])

        actual = binder.find_rule('two_type', BindingContext())

        assert actual is None

    @staticmethod
    @mark.parametrize('args', _binding_args)
    def test_passes_args_to_rule(args: dict):
        """find_rule() should pass right arguments to rule.suitable()"""
        rule = TestRule(True)
        binder = _create_binder(BINDING_TYPE, [rule])

        actual = binder.find_rule(BINDING_TYPE, BindingContext(args))

        assert args == actual.suitable_args

    @staticmethod
    def test_raises_if_rule_not_found():
        """apply() should raise error if rule is not found"""
        binder = Binder()

        with raises(BindingError):
            binder.apply('some_type', BindingContext())

    @staticmethod
    @mark.parametrize('rules, rule_index', [
        [[TestRule(True), TestRule(True)], 1],
        [[TestRule(False), TestRule(True)], 1],
        [[TestRule(True), TestRule(False)], 0]
    ])
    def test_applies_found_rule(rules, rule_index):
        """apply() should call rule.apply() for found rule"""
        binder = _create_binder(BINDING_TYPE, rules)
        expected = rules[rule_index]

        binder.apply(BINDING_TYPE, BindingContext())

        assert expected.apply_args is not None

    @staticmethod
    @mark.parametrize('args', _binding_args)
    def test_pass_args_to_rule_apply(args):
        """apply() should pass right arguments to rule.apply()"""
        rule = TestRule(True)
        binder = _create_binder(BINDING_TYPE, [rule])

        binder.apply(BINDING_TYPE, BindingContext(args))

        assert args == rule.apply_args

    @staticmethod
    @mark.parametrize('binding', [None, Mock()])
    def test_adds_binding_to_node(binding):
        """apply() should add binding to node"""
        binder = _create_binder(BINDING_TYPE, [TestRule(True, binding)])
        node = Mock()

        binder.apply(BINDING_TYPE, BindingContext({'node': node}))

        expected_call = call(binding) if binding else None
        assert node.add_binding.call_args == expected_call