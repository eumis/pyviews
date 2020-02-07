"""Binding and BindingTarget default implementations"""

from functools import partial
from re import compile as compile_regex
from typing import Any

from pyviews.binding import BindingContext
from pyviews.compilation import Expression, ObjectNode, execute
from pyviews.core import BindingError
from pyviews.core import BindingTarget
from pyviews.core import InheritedDict


def run_once(context: BindingContext):
    value = execute(context.expression_body, context.node.node_globals.to_dictionary())
    context.modifier(context.node, context.xml_attr.name, value)


PROPERTY_EXPRESSION_REGEX = compile_regex(r'([a-zA-Z_0-9]{1,}\.){0,}([a-zA-Z_0-9]{1,})')


def get_expression_target(expression: Expression, expr_vars: InheritedDict) -> BindingTarget:
    """Factory method to create expression target"""
    root = expression.get_object_tree()
    if len(root.children) != 1 or not PROPERTY_EXPRESSION_REGEX.fullmatch(expression.code):
        error = BindingError('Expression should be property expression')
        error.add_info('Expression', expression.code)
        raise error
    if root.children[0].children:
        return get_update_property_expression(expression, expr_vars)
    return get_update_global_value(expression, expr_vars)


def get_update_property_expression(expression: Expression, expr_globals: InheritedDict) -> BindingTarget:
    var_tree = expression.get_object_tree()
    _validate_property_expression(var_tree, expression.code)
    return partial(_on_property_expression_update, var_tree, expr_globals)


def _on_property_expression_update(_var_tree: ObjectNode, _vars: InheritedDict, value: Any):
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


def _validate_property_expression(var_tree: ObjectNode, source_code: str):
    if len(var_tree.children) != 1 or not var_tree.children[0].children:
        error = BindingError('Expression should be property expression')
        error.add_info('Expression', source_code)
        raise error


def get_update_global_value(expression: Expression, expr_vars: InheritedDict) -> BindingTarget:
    _validate_global_value_expression(expression.get_object_tree(), expression.code)
    return partial(_on_global_value_update, expr_vars, expression.code)


def _validate_global_value_expression(root: ObjectNode, source_code: str):
    if len(root.children) != 1 or root.children[0].children:
        error = BindingError('Expression should be dictionary key')
        error.add_info('Expression', source_code)
        raise error


def _on_global_value_update(_vars: InheritedDict, key: str, value):
    _vars[key] = value
