from pyviews.core.observable import Observable
from pyviews.core.compilation import Expression, ExpressionVars, Entry

class Dependency:
    def __init__(self, observable: Observable, key, callback):
        self._observable = observable
        self._key = key
        self._callback = callback

    def destroy(self):
        self._observable.release(self._key, self._callback)
        self._observable = None
        self._key = None
        self._callback = None

class BindingTarget:
    def __init__(self, instance, prop, modifier):
        self._instance = instance
        self._property = prop
        self._modifier = modifier

    def set_value(self, value):
        self._modifier(self._instance, self._property, value)

class Binding:
    def __init__(self, target: BindingTarget, expression: Expression):
        self._target = target
        self._expression = expression
        self._dependencies = []
        self._vars = None

    def bind(self, expr_vars: ExpressionVars):
        self.destroy()
        self._vars = expr_vars
        var_tree = self._expression.get_var_tree()
        self._create_dependencies(expr_vars, var_tree)
        self._update_target()

    def _create_dependencies(self, inst, var_tree: Entry):
        try:
            if isinstance(inst, Observable):
                for entry in var_tree.entries:
                    inst.observe(entry.key, self._update_callback)
        except KeyError:
            pass
        for entry in var_tree.entries:
            child_inst = self._get_child(inst, entry.key)
            if child_inst is not None:
                self._create_dependencies(child_inst, entry)

    def _get_child(self, inst, key):
        try:
            return inst[key] if isinstance(inst, ExpressionVars) \
                         else getattr(inst, key)
        except KeyError:
            return None

    def _update_callback(self, new_val, old_val):
        if isinstance(new_val, Observable) or isinstance(old_val, Observable):
            self.bind(self._vars)
        else:
            self._update_target()

    def _update_target(self):
        value = self._expression.execute(self._vars.to_all_dictionary())
        self._target.set_value(value)

    def destroy(self):
        self._vars = None
        for dependency in self._dependencies:
            dependency.destroy()
        self._dependencies = []

class TwoWaysBinding:
    def __init__(self, target: BindingTarget, expression: Expression):
        self._to_view = Binding(target, expression)
        self._to_vm = None
        self._expression = expression
        self._vars = None

    def bind(self, expr_vars: ExpressionVars):
        self.destroy()
        self._vars = expr_vars
        self._to_vm = self._create_to_vm(expr_vars)
        self._to_vm.bind(ExpressionVars())

    def _create_to_vm(self, expr_vars):
        target = self._get_vm_target(expression)
        self._to_vm = Binding(target, PropertyExpression(target.get_inst(), target.get_prop()))

    def _get_vm_target(self, expression):
        entry = expression.get_var_tree()
        vm = entry.entries[0].key

    def destroy(self):
        self._to_view.destroy()
        self._to_vm.destroy()
        self._vars = None
