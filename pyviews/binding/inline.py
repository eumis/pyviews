"""Inline binding"""

from functools import partial

from pyviews.binding import BindingContext
from pyviews.expression import Expression, execute
from pyviews.core import Binding, BindingCallback
from pyviews.core import InheritedDict


class InlineBinding(Binding):
    def __init__(self, callback: BindingCallback, bind_expression: Expression, value_expression: Expression,
                 expr_vars: InheritedDict):
        super().__init__()
        self._callback: BindingCallback = callback
        self._bind_expression: Expression = bind_expression
        self._value_expression: Expression = value_expression
        self._expression_vars = expr_vars

        self._destroy = None

    def bind(self):
        self.destroy()
        bind = execute(self._bind_expression, self._expression_vars.to_dictionary())
        self._execute_callback()
        self._destroy = bind(self._execute_callback)

    def _execute_callback(self):
        value = execute(self._value_expression, self._expression_vars.to_dictionary())
        self._callback(value)

    def destroy(self):
        if self._destroy:
            self._destroy()
            self._destroy = None


def bind_inline(context: BindingContext) -> InlineBinding:
    """should create InlineBinding using binding context"""
    (bind_body, value_body) = context.expression_body.split('}:{')
    bind_expr = Expression(bind_body)
    value_expr = Expression(value_body)
    on_update = partial(context.setter, context.node, context.xml_attr.name)
    binding = InlineBinding(on_update, bind_expr, value_expr, context.node.node_globals)
    binding.bind()
    return binding
