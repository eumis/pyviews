"""Binding rules and factory"""
from functools import partial

from pyviews.binding.binder import BindingRule, BindingContext
from pyviews.compilation import Expression, execute
from .implementations import ExpressionBinding, InlineBinding
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

    def apply(self, context: BindingContext) -> Binding:
        expr = Expression(context.expression_body)
        on_update = partial(context.modifier, context.node, context.xml_attr.name)
        binding = ExpressionBinding(on_update, expr, context.node.node_globals)
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
        on_update = partial(context.modifier, context.node, context.xml_attr.name)
        binding = InlineBinding(on_update, bind_expr, value_expr, context.node.node_globals)
        binding.bind()
        return binding
