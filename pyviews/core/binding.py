'''Classes used for binding'''

from pyviews.core.observable import Observable, InheritedDict
from pyviews.core.compilation import Expression, ObjectNode

class Dependency:
    '''Incapsulates observable subscription'''
    def __init__(self, observable: Observable, key, callback):
        self._observable = observable
        self._key = key
        self._callback = callback

    def destroy(self):
        '''Unsubscribes callback from observable'''
        self._observable.release(self._key, self._callback)
        self._observable = None
        self._key = None
        self._callback = None

class BindingTarget:
    '''Target for changes, applied when binding has triggered changes'''
    def change(self, value):
        '''Called to apply changes'''
        raise NotImplementedError('Targe')

class InstanceTarget(BindingTarget):
    '''Instance modifier is called on change'''
    def __init__(self, instance, prop, modifier):
        self.inst = instance
        self.prop = prop
        self._modifier = modifier

    def change(self, value):
        '''Calles modifier on instance with passed value'''
        self._modifier(self.inst, self.prop, value)

class ExpressionBinding:
    '''Binds target to expression result'''
    def __init__(self, target: BindingTarget, expression: Expression):
        self._target = target
        self._expression = expression
        self._dependencies = []
        self._vars = None

    def bind(self, expr_vars: InheritedDict):
        '''Apply binding. Expression executed with passed arguments'''
        self.destroy()
        self._vars = expr_vars
        expr_tree = self._expression.get_object_tree()
        self._create_dependencies(expr_vars, expr_tree)
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

    def _get_child(self, inst, key):
        try:
            return inst[key] if isinstance(inst, InheritedDict) \
                         else getattr(inst, key)
        except KeyError:
            return None

    def _update_callback(self, new_val, old_val):
        if isinstance(new_val, Observable) or isinstance(old_val, Observable):
            self.bind(self._vars)
        else:
            self._update_target()

    def _update_target(self):
        value = self._expression.execute(self._vars.to_dictionary())
        self._target.change(value)

    def destroy(self):
        self._vars = None
        for dependency in self._dependencies:
            dependency.destroy()
        self._dependencies = []

class ExpressionTarget:
    def __init__(self, expression):
        self._var_tree = expression.get_object_tree()
        self._validate()

    def _validate(self):
        if len(self._var_tree.children) != 1 or not self._var_tree.children[0].children:
            raise ValueError('expression should be property expression')

    def change(self, expr_vars: InheritedDict, value):
        (inst, prop) = self._get_target(expr_vars)
        setattr(inst, prop, value)

    def _get_target(self, expr_vars: InheritedDict):
        entry = self._var_tree.children[0]
        inst = expr_vars[entry.key]
        next_key = entry.children[0].key
        entry = entry.children[0]

        while entry.children:
            inst = getattr(inst, next_key)
            next_key = entry.children[0].key
            entry = entry.children[0]

        return (inst, next_key)

class ObservableBinding:
    def __init__(self, target: ExpressionTarget, observable: Observable, prop, converter):
        self._target = target
        self._observable = observable
        self._prop = prop
        self._expr_vars = None
        self._converter = converter if converter is not None else lambda value: value

    def bind(self, expr_vars: InheritedDict):
        self. destroy()
        self._expr_vars = expr_vars
        self._observable.observe(self._prop, self._update_callback)

    def _update_callback(self, new_val, old_val):
        self._update_target(new_val)

    def _update_target(self, value):
        self._target.change(self._expr_vars, self._converter(value))

    def destroy(self):
        self._observable.release(self._prop, self._update_callback)
        self._expr_vars = None

class TwoWaysBinding:
    def __init__(self, inst: Observable, prop, modifier, converter, expression: Expression):
        self._expr_binding = \
            ExpressionBinding(InstanceTarget(inst, prop, modifier), expression)
        self._observ_binding = \
            ObservableBinding(ExpressionTarget(expression), inst, prop, converter)
        self._vars = None

    def bind(self, expr_vars: InheritedDict):
        self.destroy()
        self._expr_binding.bind(expr_vars)
        self._observ_binding.bind(expr_vars)

    def destroy(self):
        self._expr_binding.destroy()
        self._observ_binding.destroy()
