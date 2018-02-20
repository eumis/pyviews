from unittest import TestCase, main
from tests.utility import case
from pyviews.core.binding import BindingError
from pyviews.rendering.binding import BindingFactory, BindingArgs, add_default_rules
from pyviews.rendering.binding import apply_once, apply_oneway, apply_twoways

class BindingFactoryTests(TestCase):
    def setUp(self):
        self.factory = BindingFactory()
        self.args = BindingArgs(None, None, None, None)

    @case([True, True], 0)
    @case([False, True], 1)
    @case([False, True, False], 1)
    @case([False, True, True], 1)
    @case([False, False, True], 2)
    def test_get_apply_returns_first_suitable(self, suitables, rule_index):
        factory = BindingFactory()
        args = BindingArgs(None, None, None, None)

        binding_type = 'type'
        rules = [BindingFactory.Rule(lambda args, s=suitable: s, lambda binding_type, args: None) \
                 for suitable in suitables]

        for rule in rules:
            factory.add_rule(binding_type, rule)
        actual_apply = factory.get_apply(binding_type, args)

        msg = 'get_apply should return first suitable apply'
        self.assertEqual(rules[rule_index].apply, actual_apply, msg=msg)

    def test_get_apply_raises(self):
        msg = 'BindingFactory should raise BindingError if there is no suitable rule'
        with self.assertRaises(BindingError, msg=msg):
            self.factory.get_apply('type', self.args)

class DefaultRulesTests(TestCase):
    @case('once', apply_once)
    @case('oneway', apply_oneway)
    @case('twoways', apply_twoways)
    def test_add_default_rules(self, binding_type, apply):
        factory = BindingFactory()
        args = BindingArgs(None, None, None, None)
        add_default_rules(factory)

        actual_apply = factory.get_apply(binding_type, args)

        msg = 'add_default_rules should add default rules'
        self.assertEqual(apply, actual_apply, msg=msg)

if __name__ == '__main__':
    main()
