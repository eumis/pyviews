"""Binding rules and factory"""
from pyviews.binding.binder import BindingRule, BindingContext
from pyviews.compilation import Expression, execute
from .implementations import ExpressionBinding, PropertyTarget, InlineBinding
from ..core import Binding


class OnceRule(BindingRule):
    """Applies "once" binding - expression result is assigned to property without binding"""

    def suitable(self, _: BindingContext) -> bool:
        return True

    def apply(self, context: BindingContext) -> None:
        value = execute(context.expression_body, context.node.node_globals.to_dictionary())
        context.modifier(context.node, context.xml_attr.name, value)


class OnewayRule(BindingRule):
    """Applies "oneway" binding"""

    def suitable(self, _: BindingContext) -> bool:
        return True

    def apply(self, context: BindingContext):
        expr = Expression(context.expression_body)
        target = PropertyTarget(context.node, context.xml_attr.name, context.modifier)
        binding = ExpressionBinding(target, expr, context.node.node_globals)
        binding.bind()
        return binding


class InlineRule(BindingRule):
    """Applies "inline" binding"""

    def suitable(self, context: BindingContext) -> bool:
        return True

    def apply(self, context: BindingContext) -> Binding:
        (bind_body, value_body) = context.expression_body.split('}:{')
        bind_expr = Expression(bind_body)
        value_expr = Expression(value_body)
        target = PropertyTarget(context.node, context.xml_attr.name, context.modifier)
        binding = InlineBinding(target, bind_expr, value_expr, context.node.node_globals)
        binding.bind()
        return binding
