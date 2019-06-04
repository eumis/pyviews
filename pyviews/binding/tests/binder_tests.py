from unittest.mock import Mock

from pytest import mark, raises

from pyviews.core import BindingRule, BindingError
from pyviews.binding.binder import Binder

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


class BinderTests:
    @mark.parametrize('rules, rule_index', [
        [[TestRule(True), TestRule(True)], 1],
        [[TestRule(False), TestRule(True)], 1],
        [[TestRule(True), TestRule(False)], 0],
        [[TestRule(False), TestRule(False)], None]
    ])
    def test_returns_suitable_rule(self, rules, rule_index):
        """find_rule() should return first suitable rule by LIFO"""
        binder = _create_binder(BINDING_TYPE, rules)
        expected = rules[rule_index] if rule_index is not None else None

        actual = binder.find_rule(BINDING_TYPE)

        assert expected == actual

    @staticmethod
    def test_returns_rule_by_type():
        """find_rule() should return suitable rule for provided type"""
        binder = _create_binder('one_type', [TestRule(True)])

        actual = binder.find_rule('two_type')

        assert actual is None

    @mark.parametrize('args', [
        {},
        {'node': Mock()},
        {'node': Mock(), 'modifier': lambda *args: None}
    ])
    def test_passes_args_to_rule(self, args: dict):
        """find_rule() should pass right arguments to rule.suitable()"""
        rule = TestRule(True)
        binder = _create_binder(BINDING_TYPE, [rule])

        actual = binder.find_rule(BINDING_TYPE, **args)

        assert args == actual.suitable_args

    @staticmethod
    def test_raises_error_if_rule_not_found():
        """apply() should raise error if rule is not found"""
        binder = Binder()

        with raises(BindingError):
            binder.apply('some_type')

    @mark.parametrize('rules, rule_index', [
        [[TestRule(True), TestRule(True)], 1],
        [[TestRule(False), TestRule(True)], 1],
        [[TestRule(True), TestRule(False)], 0]
    ])
    def test_applies_found_rule(self, rules, rule_index):
        """apply() should call rule.apply() for found rule"""
        binder = _create_binder(BINDING_TYPE, rules)
        expected = rules[rule_index]

        binder.apply(BINDING_TYPE)

        assert expected.apply_args is not None

    @staticmethod
    @mark.parametrize('args', [
        {},
        {'node': Mock()},
        {'node': Mock(), 'modifier': lambda *args: None}
    ])
    def test_pass_args_to_rule_apply(args):
        """apply() should pass right arguments to rule.apply()"""
        rule = TestRule(True)
        binder = _create_binder(BINDING_TYPE, [rule])

        binder.apply(BINDING_TYPE, **args)

        assert args == rule.apply_args
