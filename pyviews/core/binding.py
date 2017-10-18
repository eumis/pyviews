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

class InstanceTarget:
    def __init__(self, instance, prop, modifier):
        self._instance = instance
        self._property = prop
        self._modifier = modifier

    def set_value(self, value):
        self._modifier(self._instance, self._property, value)

class ExpressionBinding:
    def __init__(self, target: InstanceTarget, expression: Expression):
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
                    self._dependencies.append(Dependency(inst, entry.key, self._update_callback))
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

class ExpressionTarget:
    def __init__(self, expression):
        self._var_tree = expression.get_var_tree()
        self._validate()

    def _validate(self):
        if len(self._var_tree.entries) != 1 or not self._var_tree.entries[0].entries:
            raise ValueError('expression should be property expression')

    def set_value(self, expr_vars: ExpressionVars, value):
        (inst, prop) = self._get_target(expr_vars)
        setattr(inst, prop, value)

    def _get_target(self, expr_vars: ExpressionVars):
        entry = self._var_tree.entries[0]
        inst = expr_vars[entry.key]
        next_key = entry.entries[0].key
        entry = entry.entries[0]

        while entry.entries:
            inst = getattr(inst, next_key)
            next_key = entry.entries[0].key
            entry = entry.entries[0]

        return (inst, next_key)

class Bindable:
    def get_variable(self, key, modifier=None):
        pass

class BindableVariable:
    def observe(self, callback):
        pass

    def release(self):
        pass

    def get_value(self):
        pass

    def set_value(self, value):
        pass

class VarBinding:
    def __init__(self, target: ExpressionTarget, var: BindableVariable):
        self._target = target
        self._var = var
        self._expr_vars = None

    def bind(self, expr_vars: ExpressionVars):
        self. destroy()
        self._expr_vars = expr_vars
        self._var.observe(self._update_callback)

    def _update_callback(self, new_val, old_val):
        self._update_target(new_val)

    def _update_target(self, value):
        self._target.set_value(self._expr_vars, value)

    def destroy(self):
        self._var.release()
        self._expr_vars = None

class TwoWaysBinding:
    def __init__(self, inst: Bindable, prop, modifier, expression: Expression):
        var = inst.get_variable(prop, modifier)
        self._expr_binding = ExpressionBinding(var, expression)
        self._prop_binding = VarBinding(ExpressionTarget(expression), var)
        self._vars = None

    def bind(self, expr_vars: ExpressionVars):
        self.destroy()
        self._expr_binding.bind(expr_vars)
        self._prop_binding.bind(expr_vars)

    def destroy(self):
        self._expr_binding.destroy()
        self._prop_binding.destroy()
