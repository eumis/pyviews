#pylint: disable=C0111,W0221,C0103

from unittest import TestCase, main
from unittest.mock import Mock, call
from pyviews.testing import case
from pyviews.core.xml import XmlAttr
from pyviews.core.binding import BindingError, Binding
from pyviews.core.observable import InheritedDict
from pyviews.rendering.binding import Binder, BindingRule, add_default_rules
from pyviews.rendering.binding import OnceRule, OnewayRule

BINDING_TYPE = 'default_binding_type'

class TestRule(BindingRule):
    def __init__(self, suitable: bool):
        self._suitable = suitable
        self.suitable_args = None
        self.apply_args = None

    def suitable(self, **args):
        self.suitable_args = args
        return self._suitable

    def apply(self, **args):
        self.apply_args = args

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

class Binder_find_rule_tests(TestCase):
    @case([TestRule(True), TestRule(True)])
    @case([TestRule(False), TestRule(True)])
    @case([TestRule(True), TestRule(False)])
    @case([TestRule(False), TestRule(False)])
    def test_returns_suitable_rule(self, rules):
        binder = _create_binder(BINDING_TYPE, rules)

        expected = _find_suitable_rule(rules)

        actual = binder.find_rule(BINDING_TYPE)

        msg = 'should return last added suitable rule'
        self.assertEqual(expected, actual, msg)

    def _add_rules(self, rules, binder, binding_type):
        for rule in rules:
            binder.add_rule(binding_type, rule)

    def test_returns_rule_by_type(self):
        one_type = 'one_type'
        two_type = 'two_type'
        binder = _create_binder(one_type, [TestRule(True)])

        actual = binder.find_rule(two_type)

        msg = 'should find rule for passed binding type'
        self.assertIsNone(actual, msg)

    @case({})
    @case({'node': Mock()})
    @case({'node': Mock(), 'modifier': lambda *args: None})
    def test_passes_args_to_rule(self, args: dict):
        rule = TestRule(True)
        binder = _create_binder(BINDING_TYPE, [rule])

        actual = binder.find_rule(BINDING_TYPE, **args)

        msg = 'should pass args to suitable method of rule'
        self.assertDictEqual(args, actual.suitable_args, msg)

class Binder_apply_tests(TestCase):
    def test_raises_error_if_rule_not_found(self):
        binder = Binder()

        msg = 'should raise BindingError if rule is not found'
        with self.assertRaises(BindingError, msg=msg):
            binder.apply('some_type')

    @case([TestRule(True), TestRule(True)])
    @case([TestRule(False), TestRule(True)])
    @case([TestRule(True), TestRule(False)])
    def test_applies_found_rule(self, rules):
        binder = _create_binder(BINDING_TYPE, rules)
        expected = _find_suitable_rule(rules)

        binder.apply(BINDING_TYPE)

        msg = 'should find rule and call apply'
        self.assertIsNotNone(expected.apply_args, msg)

    @case({})
    @case({'node': Mock()})
    @case({'node': Mock(), 'modifier': lambda *args: None})
    def test_pass_args_to_rule_apply(self, args):
        rule = TestRule(True)
        binder = _create_binder(BINDING_TYPE, [rule])

        binder.apply(BINDING_TYPE, **args)

        msg = 'should pass args to apply method of rule'
        self.assertDictEqual(args, rule.apply_args, msg)

class add_default_rules_tests(TestCase):
    @case('once', OnceRule)
    @case('oneway', OnewayRule)
    def test_adds_default_rules(self, binding_type, rule_type):
        binder = Binder()

        add_default_rules(binder)
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

        rule.apply(node=node, expr_body=expr_body, modifier=modifier, attr=xml_attr)
        modifier.reset_mock()

        node.node_globals['key'] = expected_value

        msg = 'should bind property modifier to expression'
        self.assertEqual(call(node, xml_attr.name, expected_value), modifier.call_args, msg)

    def test_adds_binding_to_node(self):
        rule = OnewayRule()
        node = Mock(node_globals=InheritedDict())

        rule.apply(node=node, expr_body='None', modifier=Mock(), attr=Mock())

        msg = 'should add binding to node'
        self.assertTrue(node.add_binding.called, msg)

        actual_binding = node.add_binding.call_args[0][0]
        self.assertIsInstance(actual_binding, Binding, msg)

if __name__ == '__main__':
    main()
