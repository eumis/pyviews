"""Two ways binding"""

from functools import partial
from re import compile as compile_regex
from typing import Any

from pyviews.expression import Expression, ObjectNode
from pyviews.core import BindingError, Binding
from pyviews.core import BindingCallback
from pyviews.core import InheritedDict


class TwoWaysBinding(Binding):
    """Wrapper under two passed bindings"""

    def __init__(self, one: Binding, two: Binding):
        self._one = one
        self._two = two
        super().__init__()

    def bind(self):
        self.destroy()
        self._one.bind()
        self._two.bind()

    def destroy(self):
        self._one.destroy()
        self._two.destroy()


PROPERTY_EXPRESSION_REGEX = compile_regex(r'([a-zA-Z_0-9]{1,}\.){0,}([a-zA-Z_0-9]{1,})')


def get_expression_callback(expression: Expression, expr_vars: InheritedDict) -> BindingCallback:
    """Returns callback that sets value to property expression"""
    _validate_property_expression(expression.code)
    object_tree = expression.get_object_tree()
    if object_tree.children[0].children:
        return partial(_property_expression_callback, object_tree, expr_vars)
    return partial(_on_global_value_update, expr_vars, expression.code)


def _validate_property_expression(source_code: str):
    if not PROPERTY_EXPRESSION_REGEX.fullmatch(source_code):
        error = BindingError('Expression should be property expression')
        error.add_info('Expression', source_code)
        raise error


def _property_expression_callback(_var_tree: ObjectNode, _vars: InheritedDict, value: Any):
    (inst, prop) = _get_target(_var_tree, _vars)
    setattr(inst, prop, value)


def _get_target(var_tree: ObjectNode, expr_vars: InheritedDict):
    entry = var_tree.children[0]
    inst = expr_vars[entry.key]
    next_key = entry.children[0].key
    entry = entry.children[0]

    while entry.children:
        inst = getattr(inst, next_key)
        next_key = entry.children[0].key
        entry = entry.children[0]

    return inst, next_key


def _on_global_value_update(_vars: InheritedDict, key: str, value):
    _vars[key] = value
