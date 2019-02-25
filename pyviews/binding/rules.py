'''Binding rules and factory'''

from pyviews.core.compilation import Expression
from pyviews.core.node import Node
from pyviews.core.xml import XmlAttr
from pyviews.binding import ExpressionBinding, PropertyTarget
from pyviews.core import BindingError
from pyviews.rendering.modifiers import Modifier

class BindingRule:
    '''Creates binding for args'''
    #pylint: disable=W0613
    def suitable(self,
                 node: Node = None,
                 expr_body: str = None,
                 modifier: Modifier = None,
                 attr: XmlAttr = None,
                 **args) -> bool:
        '''Returns True if rule is suitable for args'''
        return True

    def apply(self,
              node: Node = None,
              expr_body: str = None,
              modifier: Modifier = None,
              attr: XmlAttr = None,
              **args):
        '''Applies binding'''
        raise NotImplementedError

class Binder:
    '''Applies binding'''
    def __init__(self):
        self._rules = {}

    def add_rule(self, binding_type: str, rule: BindingRule):
        '''Adds new rule'''
        if binding_type not in self._rules:
            self._rules[binding_type] = []

        self._rules[binding_type].insert(0, rule)

    def find_rule(self, binding_type: str, **args):
        '''Finds rule by binding type and args'''
        try:
            rules = self._rules[binding_type]
            return next(rule for rule in rules if rule.suitable(**args))
        except (KeyError, StopIteration):
            return None

    def apply(self, binding_type, **args):
        '''Returns apply function'''
        rule = self.find_rule(binding_type, **args)
        if rule is None:
            error = BindingError('Binding rule is not found')
            error.add_info('Binding type', binding_type)
            error.add_info('args', args)
            raise error
        binding = rule.apply(**args)
        if binding:
            args['node'].add_binding(rule.apply(**args))

class OnceRule(BindingRule):
    '''Applies "once" binding - expression result is assigned to property without binding'''
    def apply(self,
              node: Node = None,
              expr_body: str = None,
              modifier: Modifier = None,
              attr: XmlAttr = None,
              **args):
        value = Expression(expr_body).execute(node.node_globals.to_dictionary())
        modifier(node, attr.name, value)

class OnewayRule(BindingRule):
    '''Applies "oneway" binding'''
    def apply(self,
              node: Node = None,
              expr_body: str = None,
              modifier: Modifier = None,
              attr: XmlAttr = None,
              **args):
        expression = Expression(expr_body)
        target = PropertyTarget(node, attr.name, modifier)
        binding = ExpressionBinding(target, expression, node.node_globals)
        binding.bind()
        node.add_binding(binding)

def add_default_rules(binder: Binder):
    '''Adds default binding rules to passed binder'''
    binder.add_rule('once', OnceRule())
    binder.add_rule('oneway', OnewayRule())
