'''Classes used for binding'''

from pyviews.core import CoreError
from pyviews.core.observable import Observable, InheritedDict
from pyviews.core.compilation import Expression, ObjectNode

class BindingError(CoreError):
    '''Base error for binding errors'''
    pass

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
    def on_change(self, value):
        '''Called to apply changes'''
        raise NotImplementedError('{0}.on_change'.format(self.__class__.__name__))

class Binding:
    '''Binds BindingTarget to changes'''
    def bind(self):
        '''Applies binding'''
        raise NotImplementedError('Binding.bind')

    def destroy(self):
        '''Destroys binding'''
        raise NotImplementedError('Binding.destroy')

class InstanceTarget(BindingTarget):
    '''Instance modifier is called on change'''
    def __init__(self, instance, prop, modifier):
        self.inst = instance
        self.prop = prop
        self._modifier = modifier

    def on_change(self, value):
        '''Calles modifier on instance with passed value'''
        self._modifier(self.inst, self.prop, value)

class ExpressionBinding(Binding):
    '''Binds target to expression result'''
    def __init__(self, target: BindingTarget, expression: Expression, expr_vars: InheritedDict):
        self._target = target
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

    def _get_child(self, inst, key):
        try:
            return inst[key] if isinstance(inst, InheritedDict) \
                         else getattr(inst, key)
        except KeyError:
            return None

    def _update_callback(self, new_val, old_val):
        if isinstance(new_val, Observable) or isinstance(old_val, Observable):
            self.bind()
        else:
            self._update_target()

    def _update_target(self):
        value = self._expression.execute(self._vars.to_dictionary())
        self._target.on_change(value)

    def destroy(self):
        for dependency in self._dependencies:
            dependency.destroy()
        self._dependencies = []

class PropertyExpressionTarget(BindingTarget):
    '''Property is set on change. Instance and property are passed as string pass'''
    def __init__(self, expression, expr_vars: InheritedDict):
        self._var_tree = expression.get_object_tree()
        self._validate()
        self._vars = expr_vars

    def _validate(self):
        if len(self._var_tree.children) != 1 or not self._var_tree.children[0].children:
            raise BindingError('expression should be property expression')

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

        return (inst, next_key)

class ObservableBinding(Binding):
    '''Binds target to observable property'''
    def __init__(self, target: BindingTarget, observable: Observable, prop, converter):
        self._target = target
        self._observable = observable
        self._prop = prop
        self._converter = converter if converter is not None else lambda value: value

    def bind(self):
        self. destroy()
        self._observable.observe(self._prop, self._update_callback)

    def _update_callback(self, new_val, old_val):
        self._update_target(new_val)

    def _update_target(self, value):
        self._target.on_change(self._converter(value))

    def destroy(self):
        self._observable.release(self._prop, self._update_callback)

class TwoWaysBinding(Binding):
    '''Wrapper under two passed bindings'''
    def __init__(self, one: Binding, two: Binding):
        self._one = one
        self._two = two

    def bind(self):
        self.destroy()
        self._one.bind()
        self._two.bind()

    def destroy(self):
        self._one.destroy()
        self._two.destroy()
