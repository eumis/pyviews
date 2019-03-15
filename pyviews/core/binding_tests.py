#pylint: disable=missing-docstring,invalid-name

from unittest import TestCase
from unittest.mock import Mock
from pyviews.testing import case
from .binding import Binder, BindingRule, BindingError

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

    @staticmethod
    def _add_rules(rules, binder, binding_type):
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