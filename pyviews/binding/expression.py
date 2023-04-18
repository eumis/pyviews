"""Expression binding"""

from functools import partial
from typing import Any, Callable, List, Set, Union

from pyviews.binding.binder import BindingContext
from pyviews.core.bindable import Bindable, BindableRecord, recording
from pyviews.core.binding import Binding, BindingCallback, BindingError
from pyviews.core.error import PyViewsError, error_handling
from pyviews.core.expression import Expression, execute
from pyviews.core.rendering import NodeGlobals


class ExpressionBinding(Binding):
    """Binds target to expression result"""

    def __init__(self, callback: BindingCallback, expression: Expression, expr_vars: NodeGlobals):
        super().__init__()
        self._callback: BindingCallback = callback
        self._expression: Expression = expression
        self._destroy_functions: List[Callable] = []
        self._vars: NodeGlobals = expr_vars

    def bind(self, execute_callback = True):
        self.destroy()
        with recording() as records:
            value = execute(self._expression, self._vars)
        with error_handling(BindingError, self._add_error_info):
            self._create_dependencies(records)
        if execute_callback:
            self._callback(value)

    def _create_dependencies(self, records: Set[BindableRecord]):
        for record in records:
            self._subscribe_for_changes(record.bindable, record.key)

    def _subscribe_for_changes(self, inst: Bindable, key: str):
        try:
            inst.observe(key, self._update_callback)
            self._destroy_functions.append(partial(inst.release, key, self._update_callback))
        except KeyError:
            pass

    def _update_callback(self, new_val, old_val):
        with error_handling(BindingError, self._add_error_info):
            if isinstance(new_val, Bindable) or isinstance(old_val, Bindable):
                self.bind()
            else:
                self._execute_callback()

    def _add_error_info(self, error: PyViewsError):
        error.add_info('Binding', self)
        error.add_info('Expression', self._expression.code)
        error.add_info('Callback', self._callback)

    def _execute_callback(self):
        value = execute(self._expression, self._vars)
        self._callback(value)

    def destroy(self):
        for destroy in self._destroy_functions:
            destroy()
        self._destroy_functions = []


def bind_setter_to_expression(context: BindingContext) -> Binding:
    """Binds callback to expression result changes"""
    expr = Expression(context.expression_body)
    callback = partial(context.setter, context.node, context.xml_attr.name)
    binding = ExpressionBinding(callback, expr, context.node.node_globals)
    binding.bind()
    return binding


def get_expression_callback(expression: Union[str, Expression], expr_vars: NodeGlobals) -> BindingCallback:
    """Returns callback that sets value to property expression"""
    if isinstance(expression, Expression):
        expression = expression.code
    set_expression = Expression(f'{expression} = _expression_callback_value', 'exec')
    return partial(_expression_callback, set_expression, expr_vars)


def _expression_callback(expression: Expression, node_globals: NodeGlobals, value: Any):
    node_globals['_expression_callback_value'] = value
    execute(expression, node_globals)
    node_globals.pop('_expression_callback_value')
