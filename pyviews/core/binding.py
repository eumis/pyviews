from pyviews.core.observable import Observable, ObservableEnt
from pyviews.core.compilation import Expression, ExpressionVars

class PropertyGetRecorder:
    def __init__(self, view_model: ObservableEnt):
        self._view_model = view_model
        self._used_props = set()
        self._recorders = {}

    def __getattribute__(self, prop):
        if prop in ['_view_model', '_used_props', '_recorders', 'get_used_properties']:
            return object.__getattribute__(self, prop)
        if self._view_model is not None:
            self._used_props.add(prop)
            value = getattr(self._view_model, prop)
            if isinstance(value, Observable):
                if value not in self._recorders:
                    self._recorders[value] = PropertyGetRecorder(value)
                value = self._recorders[value]
            return value

    def get_used_properties(self):
        used_props = {self._view_model: self._used_props}
        return _merge_used_properties(used_props, self._recorders.values())

def _merge_used_properties(used_props, recorders):
    for recorder in recorders:
        for vml, props in recorder.get_used_properties().items():
            used_props[vml] = used_props[vml].union(props) if vml in used_props \
                                 else props
    return {vml: props for vml, props in used_props.items() if props}

class KeyGetRecorder(dict):
    def __init__(self, mapping):
        super().__init__(mapping)
        self._used_keys = set()

    def __getitem__(self, key):
        self._used_keys.add(key)
        return dict.__getitem__(self, key)

    def get_used_keys(self):
        return self._used_keys.copy()

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
        recorder = self._get_parameters_recorder(expr_vars.to_all_dictionary())
        value = self._expression.compile(recorder)
        used_vars = {key: recorder[key] for key in recorder.get_used_keys()}
        self._create_dependencies(expr_vars, used_vars)
        self._target.set_value(value)

    def _get_parameters_recorder(self, parameters):
        for key, value in parameters.items():
            if isinstance(value, ObservableEnt):
                parameters[key] = PropertyGetRecorder(value)
        return KeyGetRecorder(parameters)

    def _create_dependencies(self, expr_vars: ExpressionVars, used_vars):
        recorders = [(key, used_vars[key]) for key in used_vars \
                     if isinstance(used_vars[key], PropertyGetRecorder)]
        for key, recorder in set(recorders):
            expr_vars.observe(key, self._update_callback)
            used_properties = recorder.get_used_properties()
            for view_model, props in used_properties.items():
                for prop in props:
                    view_model.observe(prop, self._update_callback)
                    self._dependencies.append((view_model, prop))

    def _get_used_properties(self, parameters):
        recorders = [value for value in parameters.values() \
                     if isinstance(value, PropertyGetRecorder)]
        return _merge_used_properties({}, recorders)

    def _update_callback(self, new_val, old_val):
        value = self._expression.compile(self._vars.to_all_dictionary())
        self._target.set_value(value)

    def destroy(self):
        self._vars = None
        for view_model, prop in self._dependencies:
            view_model.release(prop, self._update_callback)
        self._dependencies = []
