"""Binding and BindingTarget default implementations"""
from functools import partial
from re import compile as compile_regex
from sys import exc_info
from typing import Any

from pyviews.compilation import Expression, ObjectNode
from pyviews.core import Observable, InheritedDict
from pyviews.core import Binding, BindingTarget
from pyviews.core import ViewsError, BindingError


class Dependency:
    """Holds observable subscription"""

    def __init__(self, observable: Observable, key, callback):
        self._observable = observable
        self._key = key
        self._callback = callback

    def destroy(self):
        """Releases callback from observable"""
        self._observable.release(self._key, self._callback)
        self._observable = None
        self._key = None
        self._callback = None


class ExpressionBinding(Binding):
    """Binds target to expression result"""

    def __init__(self, on_update: BindingTarget, expression: Expression, expr_vars: InheritedDict):
        super().__init__()
        self._on_update = on_update
        self._expression = expression
        self._dependencies = []
        self._vars = expr_vars

    def bind(self):
        self.destroy()
        objects_tree = self._expression.get_object_tree()
        self._create_dependencies(self._vars, objects_tree)
        self._update_target()

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
                self._dependencies.append(Dependency(inst, entry.key, self._update_callback))
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
        try:
            if isinstance(new_val, Observable) or isinstance(old_val, Observable):
                self.bind()
            else:
                self._update_target()
        except ViewsError as error:
            self.add_error_info(error)
            raise
        except BaseException:
            info = exc_info()
            error = BindingError(BindingError.TargetUpdateError)
            self.add_error_info(error)
            error.add_cause(info[1])
            raise error from info[1]

    def _update_target(self):
        value = self._expression.execute(self._vars.to_dictionary())
        self._on_update(value)

    def destroy(self):
        for dependency in self._dependencies:
            dependency.destroy()
        self._dependencies = []


def get_update_property_expression(expression: Expression, expr_globals: InheritedDict) -> BindingTarget:
    var_tree = expression.get_object_tree()
    _validate_property_expression(var_tree, expression.code)
    return partial(_on_property_expression_update, var_tree, expr_globals)


def _validate_property_expression(var_tree: ObjectNode, source_code: str):
    if len(var_tree.children) != 1 or not var_tree.children[0].children:
        error = BindingError('Expression should be property expression')
        error.add_info('Expression', source_code)
        raise error


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


class ObservableBinding(Binding):
    """Binds to observable property"""

    def __init__(self, on_update: BindingTarget, observable: Observable, prop):
        super().__init__()
        self._on_update = on_update
        self._observable = observable
        self._prop = prop

    def bind(self):
        self.destroy()
        self._observable.observe(self._prop, self._update_callback)
        self._update_target(getattr(self._observable, self._prop))

    def _update_callback(self, new_val, _):
        try:
            self._update_target(new_val)
        except ViewsError as error:
            self.add_error_info(error)
            raise
        except BaseException:
            info = exc_info()
            error = BindingError(BindingError.TargetUpdateError)
            self.add_error_info(error)
            error.add_cause(info[1])
            raise error from info[1]

    def _update_target(self, value):
        self._on_update(value)

    def destroy(self):
        self._observable.release(self._prop, self._update_callback)


class TwoWaysBinding(Binding):
    """Wrapper under two passed bindings"""

    def __init__(self, one: Binding, two: Binding):
        self._add_error_info = None
        self._one = one
        self._two = two
        super().__init__()

    @property
    def add_error_info(self):
        """Callback to add info to error"""
        return self._add_error_info

    @add_error_info.setter
    def add_error_info(self, value):
        self._add_error_info = value
        self._one.add_error_info = value
        self._two.add_error_info = value

    def bind(self):
        self.destroy()
        self._one.bind()
        self._two.bind()

    def destroy(self):
        self._one.destroy()
        self._two.destroy()


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


class InlineBinding(Binding):
    def __init__(self, on_update: BindingTarget, bind_expression: Expression, value_expression: Expression,
                 expr_vars: InheritedDict):
        super().__init__()
        self._on_update: BindingTarget = on_update
        self._bind_expression: Expression = bind_expression
        self._value_expression: Expression = value_expression
        self._expression_vars = expr_vars

        self._destroy = None

    def bind(self):
        self.destroy()
        bind = self._bind_expression.execute(self._expression_vars.to_dictionary())
        self._update_target()
        self._destroy = bind(self._update_target)

    def _update_target(self):
        value = self._value_expression.execute(self._expression_vars.to_dictionary())
        self._on_update(value)

    def destroy(self):
        if self._destroy:
            self._destroy()
            self._destroy = None
