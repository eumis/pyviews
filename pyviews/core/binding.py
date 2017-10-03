from pyviews.core.observable import Observable, ObservableEnt
from pyviews.core.compilation import Expression, ExpressionVars, Entry

class Dependency:
    def __init__(self, prop, view_model):
        self._children = []
        self.prop = prop
        self.view_model = view_model

class DependencyTree:
    def __init__(self):
        self._children = []

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
        self._update_target()

    def _update_target(self):
        value = self._expression.execute(self._vars.to_all_dictionary())
        self._target.set_value(value)

    def destroy(self):
        self._vars = None
        for view_model, prop in self._dependencies:
            view_model.release(prop, self._update_callback)
        self._dependencies = []
