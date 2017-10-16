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
        entry = self._var_tree.entries[0]
        inst = expr_vars[entry.key]
        next_key = entry.entries[0].key
        entry = entry.entries[0]

        while entry.entries:
            inst = getattr(inst, next_key)
            next_key = entry.entries[0].key
            entry = entry.entries[0]

        setattr(inst, next_key, value)

class PropertyBinding:
    def __init__(self, target: ExpressionTarget, inst: Observable, prop):
        self._target = target
        self._inst = inst
        self._prop = prop
        self._vars = None
        self._dependencies = []

    def bind(self, expr_vars: ExpressionVars):
        self. destroy()
        self._vars = expr_vars
        self._inst.observe(self._prop, self._update_callback)
        self._dependencies.append(Dependency(self._inst, self._prop, self._update_callback))

    def _update_callback(self, new_val, old_val):
        self._update_target(new_val)

    def _update_target(self, value):
        self._target.set_value(self._vars, value)

    def destroy(self):
        self._vars = None
        for dependency in self._dependencies:
            dependency.destroy()
        self._dependencies = []

class TwoWaysBinding:
    def __init__(self, inst, prop, modifier, expression: Expression):
        self._expr_binding = ExpressionBinding(InstanceTarget(inst, prop, modifier), expression)
        self._prop_binding = PropertyBinding(ExpressionTarget(expression), inst, prop)
        self._expression = expression
        self._vars = None

    def bind(self, expr_vars: ExpressionVars):
        self.destroy()
        self._expr_binding.bind(expr_vars)
        self._prop_binding.bind(expr_vars)

    def destroy(self):
        self._expr_binding.destroy()
        self._prop_binding.destroy()
