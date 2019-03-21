#pylint: disable=missing-docstring,invalid-name

from unittest import TestCase
from unittest.mock import Mock, call
from pyviews.testing import case
from pyviews.core.ioc import Scope, register_func
from pyviews.core import XmlAttr, InheritedDict
from pyviews.core import Binding, Binder
from pyviews.compilation import CompiledExpression
from .rules import OnceRule, OnewayRule, add_one_way_rules

with Scope('rules_tests'):
    register_func('expression', CompiledExpression)

class add_default_rules_tests(TestCase):
    @case('once', OnceRule)
    @case('oneway', OnewayRule)
    def test_adds_default_rules(self, binding_type, rule_type):
        binder = Binder()

        add_one_way_rules(binder)
        actual = binder.find_rule(binding_type)

        msg = 'should add {0} rule for {1} binding type'.format(binding_type, rule_type)
        self.assertIsInstance(actual, rule_type, msg)

class OnceRule_suitable_tests(TestCase):
    @case({})
    @case({'node': Mock()})
    @case({'node': Mock(), 'modifier': lambda *args: None})
    def test_returns_true(self, args: dict):
        rule = OnceRule()

        actual = rule.suitable(**args)

        msg = 'should always return True'
        self.assertTrue(actual, msg)

class OnceRule_apply_tests(TestCase):
    @case('1+1', {}, 2)
    @case('val', {'val': 2}, 2)
    @case('val + 1', {'val': 2}, 3)
    def test_calls_passed_modifier(self, expr_body: str, node_globals: dict, expected_value):
        rule = OnceRule()
        node = Mock(node_globals=InheritedDict(node_globals))
        modifier = Mock()
        xml_attr = XmlAttr('name')

        with Scope('rules_tests'):
            rule.apply(node=node, expr_body=expr_body, modifier=modifier, attr=xml_attr)

        msg = 'should compile expression and call modifier'
        self.assertEqual(call(node, xml_attr.name, expected_value), modifier.call_args, msg)

class OnewayRule_suitable_tests(TestCase):
    @case({})
    @case({'node': Mock()})
    @case({'node': Mock(), 'modifier': lambda *args: None})
    def test_returns_true(self, args: dict):
        rule = OnewayRule()

        actual = rule.suitable(**args)

        msg = 'should always return True'
        self.assertTrue(actual, msg)

class OnewayRule_apply_tests(TestCase):
    @case('1+1', {}, 2)
    @case('val', {'val': 2}, 2)
    @case('val + 1', {'val': 2}, 3)
    def test_calls_passed_modifier(self, expr_body: str, node_globals: dict, expected_value):
        rule = OnewayRule()
        node = Mock(node_globals=InheritedDict(node_globals))
        modifier = Mock()
        xml_attr = XmlAttr('name')

        with Scope('rules_tests'):
            rule.apply(node=node, expr_body=expr_body, modifier=modifier, attr=xml_attr)

        msg = 'should compile expression and call modifier'
        self.assertEqual(call(node, xml_attr.name, expected_value), modifier.call_args, msg)

    def test_binds_property_to_expression(self):
        rule = OnewayRule()
        initial_value = 'value'
        expected_value = 'new value'

        expr_body = 'key'
        node = Mock(node_globals=InheritedDict({'key': initial_value}))
        modifier = Mock()
        xml_attr = XmlAttr('name')

        with Scope('rules_tests'):
            rule.apply(node=node, expr_body=expr_body, modifier=modifier, attr=xml_attr)
        modifier.reset_mock()

        node.node_globals['key'] = expected_value

        msg = 'should bind property modifier to expression'
        self.assertEqual(call(node, xml_attr.name, expected_value), modifier.call_args, msg)

    def test_adds_binding_to_node(self):
        rule = OnewayRule()
        node = Mock(node_globals=InheritedDict())

        with Scope('rules_tests'):
            rule.apply(node=node, expr_body='None', modifier=Mock(), attr=Mock())

        msg = 'should add binding to node'
        self.assertTrue(node.add_binding.called, msg)

        actual_binding = node.add_binding.call_args[0][0]
        self.assertIsInstance(actual_binding, Binding, msg)
