"""Inline binding"""

from functools import partial

from pyviews.binding.binder import BindingContext
from pyviews.expression import Expression, execute
from pyviews.core import Binding, BindingCallback, error_handling, BindingError, PyViewsError
from pyviews.core import InheritedDict


class InlineBinding(Binding):
    """Inline binding"""

    def __init__(self, callback: BindingCallback, bind_expression: Expression,
                 value_expression: Expression,
                 expr_vars: InheritedDict):
        super().__init__()
        self._callback: BindingCallback = callback
        self._bind_expression: Expression = bind_expression
        self._value_expression: Expression = value_expression
        self._expression_vars = expr_vars

        self._destroy = None

    def bind(self):
        self.destroy()
        with error_handling(BindingError('Error occurred during inline binding'),
                            self._add_error_info):
            bind = execute(self._bind_expression, self._expression_vars.to_dictionary())
            self._destroy = bind(self._execute_callback)
        self._execute_callback()

    def _execute_callback(self):
        with error_handling(BindingError, self._add_error_info):
            value = execute(self._value_expression, self._expression_vars.to_dictionary())
            self._callback(value)

    def _add_error_info(self, error: PyViewsError):
        error.add_info('Binding', self)
        error.add_info('Bind expression', self._bind_expression.code)
        error.add_info('Value expression', self._value_expression.code)
        error.add_info('Binding callback', self._callback)

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
