'''Binding factory and default binding creators'''

from collections import namedtuple
from pyviews.core.compilation import Expression
from pyviews.core.binding import ExpressionBinding, InstanceTarget, PropertyExpressionTarget
from pyviews.core.binding import TwoWaysBinding, ObservableBinding, BindingError
from pyviews.rendering.expression import parse_expression

class BindingFactory:
    '''Factory for getting binding applier'''

    Rule = namedtuple('BindingRule', ['suitable', 'apply'])
    Args = namedtuple('BindingArgs', ['node', 'attr', 'modifier', 'expr_body'])

    def __init__(self):
        self._defaults = {
            'once': apply_once,
            'oneway': apply_oneway,
            'twoways': apply_twoways
        }
        self._rules = {}

    def add_rule(self, binding_type, rule):
        '''Adds new rule to factory'''
        if binding_type not in self._rules:
            self._rules[binding_type] = []

        self._rules[binding_type].append(rule)

    def get_apply(self, binding_type, args):
        '''returns apply function'''
        rule = self._find_rule(binding_type, args)
        if rule is not None:
            return rule.apply

        if binding_type in self._defaults:
            return self._defaults[binding_type]

        raise BindingError('There is no rule for binding type {0}'.format(binding_type))

    def _find_rule(self, binding_type, args):
        try:
            rules = self._rules[binding_type]
            return next(rule for rule in rules if rule.suitable(args))
        except (KeyError, StopIteration):
            return None

def apply_once(args: BindingFactory.Args):
    '''Applies "once" binding - expression result is assigned to property without binding'''
    value = Expression(args.expr_body).execute(args.node.globals.to_dictionary())
    args.modifier(args.node, args.attr.name, value)

def apply_oneway(args):
    '''
    Applies "oneway" binding.
    Expression result is assigned to property.
    Property is set on expression change.
    '''
    expression = Expression(args.expr_body)
    target = InstanceTarget(args.node, args.attr.name, args.modifier)
    binding = ExpressionBinding(target, expression, args.node.globals)
    binding.bind()
    args.node.add_binding(binding)

def apply_twoways(args):
    '''
    Applies "twoways" binding.
    Expression result is assigned to property.
    Property is set on expression change.
    Wrapped instance is changed on property change
    '''
    (converter_key, expr_body) = parse_expression(args.expr_body)
    expression = Expression(expr_body)
    target = InstanceTarget(args.node, args.attr.name, args.modifier)
    expr_binding = ExpressionBinding(target, expression, args.node.globals)

    target = PropertyExpressionTarget(expression, args.node.globals)
    converter = args.node.globals[converter_key] \
                if args.node.globals.has_key(converter_key) else None
    obs_binding = ObservableBinding(target, args.node, args.attr.name, converter)

    two_ways_binding = TwoWaysBinding(expr_binding, obs_binding)
    two_ways_binding.bind()
    args.node.add_binding(two_ways_binding)
