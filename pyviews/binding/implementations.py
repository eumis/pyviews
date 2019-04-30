"""Binding and BindingTarget default implementations"""

from re import compile as compile_regex
from sys import exc_info
from typing import Any
from pyviews.core import Observable, InheritedDict
from pyviews.core import Expression, ObjectNode
from pyviews.core import Binding, BindingTarget
from pyviews.core import CoreError, BindingError


class PropertyTarget(BindingTarget):
    """Instance modifier is called on change"""

    def __init__(self, instance, prop, modifier):
        self.inst = instance
        self.prop = prop
        self._modifier = modifier

    def on_change(self, value):
        """Calls modifier on instance with passed value"""
        self._modifier(self.inst, self.prop, value)


class FunctionTarget(BindingTarget):
    """Function is called on change"""

    def __init__(self, func):
        self.func = func

    def on_change(self, value):
        self.func(value)


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

    def __init__(self, target: BindingTarget, expression: Expression, expr_vars: InheritedDict):
        super().__init__()
        self._target = target
        self._expression = expression
        self._dependencies = []
        self._vars = expr_vars

    def bind(self):
        self.destroy()
        objects_tree = self._expression.get_object_tree
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
        except CoreError as error:
            self.add_error_info(error)
            raise
        except:
            info = exc_info()
            error = BindingError(BindingError.TargetUpdateError)
            self.add_error_info(error)
            error.add_cause(info[1])
            raise error from info[1]

    def _update_target(self):
        value = self._expression.execute(self._vars.to_dictionary())
        self._target.on_change(value)

    def destroy(self):
        for dependency in self._dependencies:
            dependency.destroy()
        self._dependencies = []


class PropertyExpressionTarget(BindingTarget):
    """Property is set on change. Instance and property are defined in expression"""

    def __init__(self, expression: Expression, expr_globals: InheritedDict):
        self._expression_code = expression.code
        self._var_tree = expression.get_object_tree
        self._validate()
        self._vars = expr_globals

    def _validate(self):
        if len(self._var_tree.children) != 1 or not self._var_tree.children[0].children:
            error = BindingError('Expression should be property expression')
            error.add_info('Expression', self._expression_code)
            raise error

    def on_change(self, value):
        (inst, prop) = self._get_target()
        setattr(inst, prop, value)

    def _get_target(self):
        entry = self._var_tree.children[0]
        inst = self._vars[entry.key]
        next_key = entry.children[0].key
        entry = entry.children[0]

        while entry.children:
            inst = getattr(inst, next_key)
            next_key = entry.children[0].key
            entry = entry.children[0]

        return inst, next_key


class GlobalValueExpressionTarget(BindingTarget):
    """Global dictionary value is set on change. Key are defined in expression"""

    def __init__(self, expression: Expression, expr_vars: InheritedDict):
        root = expression.get_object_tree
        self._key = expression.code
        self._vars = expr_vars
        self._validate(root)

    def _validate(self, root):
        if len(root.children) != 1 or root.children[0].children:
            error = BindingError('Expression should be dictionary key')
            error.add_info('Expression', self._key)
            raise error

    def on_change(self, value):
        self._vars[self._key] = value


class ObservableBinding(Binding):
    """Binds target to observable property"""

    def __init__(self, target: BindingTarget, observable: Observable, prop):
        super().__init__()
        self._target = target
        self._observable = observable
        self._prop = prop

    def bind(self):
        self.destroy()
        self._observable.observe(self._prop, self._update_callback)
        self._update_target(getattr(self._observable, self._prop))

    def _update_callback(self, new_val, _):
        try:
            self._update_target(new_val)
        except CoreError as error:
            self.add_error_info(error)
            raise
        except:
            info = exc_info()
            error = BindingError(BindingError.TargetUpdateError)
            self.add_error_info(error)
            error.add_cause(info[1])
            raise error from info[1]

    def _update_target(self, value):
        self._target.on_change(value)

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
        """Callback to add info to catched error"""
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
    root = expression.get_object_tree
    if len(root.children) != 1 or not PROPERTY_EXPRESSION_REGEX.fullmatch(expression.code):
        error = BindingError('Expression should be property expression')
        error.add_info('Expression', expression.code)
        raise error
    if root.children[0].children:
        return PropertyExpressionTarget(expression, expr_vars)
    return GlobalValueExpressionTarget(expression, expr_vars)
