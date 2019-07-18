"""Binding rules and factory"""
from injectool import resolve

from pyviews.core import BindingRule, Modifier, XmlAttr, Node, Expression
from .implementations import ExpressionBinding, PropertyTarget


class OnceRule(BindingRule):
    """Applies "once" binding - expression result is assigned to property without binding"""

    def suitable(self, **args) -> bool:
        return True

    def apply(self, **args):
        node: Node = args['node']
        expr_body: str = args['expr_body']
        modifier: Modifier = args['modifier']
        attr: XmlAttr = args['attr']
        value = resolve(Expression, expr_body).execute(node.node_globals.to_dictionary())
        modifier(node, attr.name, value)


class OnewayRule(BindingRule):
    """Applies "one way" binding"""

    def suitable(self, **args) -> bool:
        return True

    def apply(self, **args):
        node: Node = args['node']
        expr_body: str = args['expr_body']
        modifier: Modifier = args['modifier']
        attr: XmlAttr = args['attr']
        expr = resolve(Expression, expr_body)
        target = PropertyTarget(node, attr.name, modifier)
        binding = ExpressionBinding(target, expr, node.node_globals)
        binding.bind()
        node.add_binding(binding)
