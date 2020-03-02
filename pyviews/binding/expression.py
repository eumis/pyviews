"""Expression binding"""

from functools import partial
from typing import Callable, List, Any

from pyviews.binding.binder import BindingContext
from pyviews.core import Binding, BindingCallback, InheritedDict, Observable, BindingError, \
    PyViewsError
from pyviews.core import error_handling
from pyviews.expression import Expression, ObjectNode, execute


class ExpressionBinding(Binding):
    """Binds target to expression result"""

    def __init__(self, callback: BindingCallback, expression: Expression, expr_vars: InheritedDict):
        super().__init__()
        self._callback: BindingCallback = callback
        self._expression: Expression = expression
        self._destroy_functions: List[Callable] = []
        self._vars: InheritedDict = expr_vars

    def bind(self):
        self.destroy()
        objects_tree = self._expression.get_object_tree()
        with error_handling(BindingError, self._add_error_info):
            self._create_dependencies(self._vars, objects_tree)
        self._execute_callback()

    def _create_dependencies(self, inst, var_tree: ObjectNode):
        if isinstance(inst, Observable):
            self._subscribe_for_changes(inst, var_tree)

        for entry in var_tree.children:
            child_inst = self._get_child(inst, entry.key)
            if child_inst is not None:
                self._create_dependencies(child_inst, entry)

    def _subscribe_for_changes(self, inst: Observable, var_tree):
        try:
            for entry in var_tree.children:
                inst.observe(entry.key, self._update_callback)
                self._destroy_functions.append(
                    partial(inst.release, entry.key, self._update_callback))
        except KeyError:
            pass

    @staticmethod
    def _get_child(inst: Any, key: str) -> Any:
        try:
            return inst[key] if isinstance(inst, InheritedDict) \
                else getattr(inst, key)
        except KeyError:
            return None

    def _update_callback(self, new_val, old_val):
        with error_handling(BindingError, self._add_error_info):
            if isinstance(new_val, Observable) or isinstance(old_val, Observable):
                self.bind()
            else:
                self._execute_callback()

    def _add_error_info(self, error: PyViewsError):
        error.add_info('Binding', self)
        error.add_info('Expression', self._expression.code)
        error.add_info('Callback', self._callback)

    def _execute_callback(self):
        value = execute(self._expression, self._vars.to_dictionary())
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
