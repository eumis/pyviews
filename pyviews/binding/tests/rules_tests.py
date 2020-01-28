from unittest.mock import Mock, call

from pytest import mark, fixture

from pyviews.binding import ExpressionBinding
from pyviews.binding.binder import BindingContext
from pyviews.core import XmlAttr, InheritedDict
from pyviews.binding.rules import OnceRule, OnewayRule, InlineRule


@fixture
def rule_params_fixture(request):
    request.cls.modifier = Mock()
    request.cls.xml_attr = XmlAttr('name')


@fixture
def once_rule_fixture(request):
    request.cls.rule = OnceRule()


_binding_args = [
    {},
    {'node': Mock()},
    {'node': Mock(), 'modifier': lambda *args: None}
]


@mark.usefixtures('once_rule_fixture', 'rule_params_fixture')
class OnceRuleTests:
    """OnceRule tests"""

    @mark.parametrize('args', _binding_args)
    def test_suitable(self, args: dict):
        """suitable() should return true"""
        assert self.rule.suitable(BindingContext(args))

    @mark.parametrize('expr_body, node_globals, expected_value', [
        ('1+1', {}, 2),
        ('val', {'val': 2}, 2),
        ('val + 1', {'val': 2}, 3)
    ])
    def test_calls_passed_modifier(self, expr_body: str, node_globals: dict, expected_value):
        """apply() should call passed modifier"""
        node = Mock(node_globals=InheritedDict(node_globals))

        self.rule.apply(BindingContext({
            'node': node,
            'expression_body': expr_body,
            'modifier': self.modifier,
            'xml_attr': self.xml_attr
        }))

        assert self.modifier.call_args == call(node, self.xml_attr.name, expected_value)


@fixture
def oneway_rule_fixture(request):
    request.cls.rule = OnewayRule()


@mark.usefixtures('oneway_rule_fixture', 'rule_params_fixture')
class OnewayRuleTests:
    """OnewayRule tests"""

    @mark.parametrize('args', _binding_args)
    def test_returns_true(self, args: dict):
        """suitable() should return true"""
        assert self.rule.suitable(BindingContext(args))

    @mark.parametrize('expr_body, node_globals, expected_value', [
        ('1+1', {}, 2),
        ('val', {'val': 2}, 2),
        ('val + 1', {'val': 2}, 3)
    ])
    def test_calls_passed_modifier(self, expr_body: str, node_globals: dict, expected_value):
        """apply() should call passed modifier"""
        node = Mock(node_globals=InheritedDict(node_globals))

        self.rule.apply(BindingContext({
            'node': node,
            'expression_body': expr_body,
            'modifier': self.modifier,
            'xml_attr': self.xml_attr
        }))

        assert self.modifier.call_args == call(node, self.xml_attr.name, expected_value)

    def test_subscribes_to_changes(self):
        """apply() should subscribe to expression changes and update property"""
        initial_value = 'value'
        new_value = 'new value'

        expr_body = 'key'
        node = Mock(node_globals=InheritedDict({'key': initial_value}))

        self.rule.apply(BindingContext({
            'node': node,
            'expression_body': expr_body,
            'modifier': self.modifier,
            'xml_attr': self.xml_attr
        }))
        self.modifier.reset_mock()

        node.node_globals['key'] = new_value

        assert self.modifier.call_args == call(node, self.xml_attr.name, new_value)

    def test_apply_returns_binding(self):
        """apply() should return expression binding"""
        node = Mock(node_globals=InheritedDict())

        actual_binding = self.rule.apply(BindingContext({
            'node': node,
            'expression_body': 'None',
            'modifier': self.modifier,
            'xml_attr': self.xml_attr
        }))

        assert isinstance(actual_binding, ExpressionBinding)


@fixture
def inline_rule_fixture(request):
    request.cls.rule = InlineRule()


@mark.usefixtures('inline_rule_fixture')
class InlineRuleTests:
    """InlineRule tests"""

    def test_suitable_returns_true(self):
        """suitable should return true"""

        assert self.rule.suitable(BindingContext())
