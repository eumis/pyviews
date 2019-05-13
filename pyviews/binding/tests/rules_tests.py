from unittest.mock import Mock, call

from pytest import mark, fixture

from pyviews.ioc import Scope, register_func
from pyviews.core import XmlAttr, InheritedDict
from pyviews.core import Binding
from pyviews.compilation import CompiledExpression
from pyviews.binding.rules import OnceRule, OnewayRule


@fixture(scope='module')
def scope_fixture():
    with Scope('rules_tests') as scope:
        register_func('expression', CompiledExpression)
        yield scope


@fixture
def rule_params_fixture(request):
    request.cls.modifier = Mock()
    request.cls.xml_attr = XmlAttr('name')


@fixture
def once_rule_fixture(request):
    request.cls.rule = OnceRule()


@mark.usefixtures('once_rule_fixture', 'rule_params_fixture', 'scope_fixture')
class OnceRuleTests:
    """OnceRule tests"""

    @mark.parametrize('args', [
        {},
        {'node': Mock()},
        {'node': Mock(), 'modifier': lambda *args: None}
    ])
    def test_suitable(self, args: dict):
        """suitable() should return true"""
        assert self.rule.suitable(**args)

    @mark.parametrize('expr_body, node_globals, expected_value', [
        ('1+1', {}, 2),
        ('val', {'val': 2}, 2),
        ('val + 1', {'val': 2}, 3)
    ])
    def test_calls_passed_modifier(self, expr_body: str, node_globals: dict, expected_value):
        """apply() should call passed modifier"""
        node = Mock(node_globals=InheritedDict(node_globals))

        self.rule.apply(node=node, expr_body=expr_body, modifier=self.modifier, attr=self.xml_attr)

        assert self.modifier.call_args == call(node, self.xml_attr.name, expected_value)


@fixture
def oneway_rule_fixture(request):
    request.cls.rule = OnewayRule()


@mark.usefixtures('oneway_rule_fixture', 'rule_params_fixture', 'scope_fixture')
class OnewayRuleTests:
    """OnewayRule tests"""

    @mark.parametrize('args', [
        {},
        {'node': Mock()},
        {'node': Mock(), 'modifier': lambda *args: None}
    ])
    def test_returns_true(self, args: dict):
        """suitable() should return true"""
        assert self.rule.suitable(**args)

    @mark.parametrize('expr_body, node_globals, expected_value', [
        ('1+1', {}, 2),
        ('val', {'val': 2}, 2),
        ('val + 1', {'val': 2}, 3)
    ])
    def test_calls_passed_modifier(self, expr_body: str, node_globals: dict, expected_value):
        """apply() should call passed modifier"""
        node = Mock(node_globals=InheritedDict(node_globals))

        self.rule.apply(node=node, expr_body=expr_body, modifier=self.modifier, attr=self.xml_attr)

        assert self.modifier.call_args == call(node, self.xml_attr.name, expected_value)

    def test_binds_property_to_expression(self):
        """apply() should subscribe to expression changes"""
        initial_value = 'value'
        new_value = 'new value'

        expr_body = 'key'
        node = Mock(node_globals=InheritedDict({'key': initial_value}))

        self.rule.apply(node=node, expr_body=expr_body, modifier=self.modifier, attr=self.xml_attr)
        self.modifier.reset_mock()

        node.node_globals['key'] = new_value

        assert self.modifier.call_args == call(node, self.xml_attr.name, new_value)

    def test_adds_binding_to_node(self):
        """apply() should add created binding to node"""
        node = Mock(node_globals=InheritedDict())

        self.rule.apply(node=node, expr_body='None', modifier=self.modifier, attr=self.xml_attr)

        assert node.add_binding.called
        actual_binding = node.add_binding.call_args[0][0]
        assert isinstance(actual_binding, Binding)
