"""Binding rules and factory"""
from injectool import resolve

from pyviews.binding.binder import BindingRule, BindingContext
from pyviews.core import Expression
from .implementations import ExpressionBinding, PropertyTarget


class OnceRule(BindingRule):
    """Applies "once" binding - expression result is assigned to property without binding"""

    def suitable(self, _: BindingContext) -> bool:
        return True

    def apply(self, context: BindingContext) -> None:
        value = resolve(Expression, context.expression_body) \
            .execute(context.node.node_globals.to_dictionary())
        context.modifier(context.node, context.xml_attr.name, value)


class OnewayRule(BindingRule):
    """Applies "one way" binding"""

    def suitable(self, _: BindingContext) -> bool:
        return True

    def apply(self, context: BindingContext):
        expr = resolve(Expression, context.expression_body)
        target = PropertyTarget(context.node, context.xml_attr.name, context.modifier)
        binding = ExpressionBinding(target, expr, context.node.node_globals)
        binding.bind()
        return binding
