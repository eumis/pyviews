'''Binding factory and default binding creators'''

from typing import Callable
from collections import namedtuple
from pyviews.core.compilation import Expression
from pyviews.core.node import Node
from pyviews.core.binding import ExpressionBinding, PropertyTarget
from pyviews.core.binding import BindingError
from pyviews.rendering.modifiers import Modifier

class BindingArgs:
    '''Binding arguments'''
    def __init__(self, **args):
        self.node: Node = args.get('node')
        self.attr: str = args.get('attr')
        self.modifier: Modifier = args.get('modifier')
        self.expr_body: str = args.get('expr_body')

class BindingRule:
    '''Binding Rule'''
    def __init__(self,
                 apply: Callable[[BindingArgs], None],
                 suitable: Callable[[BindingArgs], bool] = None):
        if suitable is None:
            suitable = lambda args: True
        self._suitable = suitable
        self._apply = apply

    def suitable(self, args: BindingArgs) -> bool:
        '''Returns True if rule is suitable for args'''
        return self._suitable(args)

    @property
    def apply(self) -> Callable[[BindingArgs], None]:
        '''Applies binding'''
        return self._apply

class BindingFactory:
    '''Factory for getting binding applier'''

    def __init__(self):
        self._rules = {}

    def add_rule(self, binding_type, rule):
        '''Adds new rule to factory'''
        if binding_type not in self._rules:
            self._rules[binding_type] = []

        self._rules[binding_type].append(rule)

    def get_apply(self, binding_type, args):
        '''returns apply function'''
        rule = self._find_rule(binding_type, args)
        if rule is None:
            error = BindingError('Binding rule is not found')
            error.add_info('Binding type', binding_type)
            error.add_info('Expression', args.expr_body)
            raise error
        return rule.apply

    def _find_rule(self, binding_type, args):
        try:
            rules = self._rules[binding_type]
            return next(rule for rule in reversed(rules) if rule.suitable(args))
        except (KeyError, StopIteration):
            return None

def apply_once(args: BindingArgs):
    '''Applies "once" binding - expression result is assigned to property without binding'''
    value = Expression(args.expr_body).execute(args.node.node_globals.to_dictionary())
    args.modifier(args.node, args.attr.name, value)

def apply_oneway(args: BindingArgs):
    '''
    Applies "oneway" binding.
    Expression result is assigned to property.
    Property is set on expression change.
    '''
    expression = Expression(args.expr_body)
    target = PropertyTarget(args.node, args.attr.name, args.modifier)
    binding = ExpressionBinding(target, expression, args.node.node_globals)
    binding.bind()
    args.node.add_binding(binding)

def add_default_rules(factory: BindingFactory):
    '''Adds default binding rules to passed factory'''
    factory.add_rule('once', BindingRule(apply_once))
    factory.add_rule('oneway', BindingRule(apply_oneway))
