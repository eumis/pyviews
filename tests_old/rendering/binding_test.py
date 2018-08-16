from unittest import TestCase, main
from pyviews.testing import case
from pyviews.core.binding import BindingError
from pyviews.rendering.binding import BindingFactory, BindingArgs, add_default_rules
from pyviews.rendering.binding import apply_once, apply_oneway

class BindingFactoryTests(TestCase):
    def setUp(self):
        self.factory = BindingFactory()
        self.args = BindingArgs(None, None, None, None)

    @case([True, True], 1)
    @case([False, True], 1)
    @case([False, True, False], 1)
    @case([False, True, True], 2)
    @case([True, False, False], 0)
    def test_get_apply_returns_first_suitable(self, suitables, rule_index):
        binding_type = 'type'
        rules = [BindingFactory.Rule(lambda args, s=suitable: s, lambda binding_type, args: None) \
                 for suitable in suitables]

        for rule in rules:
            self.factory.add_rule(binding_type, rule)
        actual_apply = self.factory.get_apply(binding_type, self.args)

        msg = 'get_apply should return first suitable apply'
        self.assertEqual(rules[rule_index].apply, actual_apply, msg=msg)

    def test_get_apply_raises(self):
        msg = 'BindingFactory should raise BindingError if there is no suitable rule'
        with self.assertRaises(BindingError, msg=msg):
            self.factory.get_apply('type', self.args)

class DefaultRulesTests(TestCase):
    @case('once', apply_once)
    @case('oneway', apply_oneway)
    def test_add_default_rules(self, binding_type, apply):
        factory = BindingFactory()
        args = BindingArgs(None, None, None, None)
        add_default_rules(factory)

        actual_apply = factory.get_apply(binding_type, args)

        msg = 'add_default_rules should add default rules'
        self.assertEqual(apply, actual_apply, msg=msg)

if __name__ == '__main__':
    main()
