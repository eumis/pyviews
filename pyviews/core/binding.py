from pyviews.core.compilation import Expression
from pyviews.core.viewmodel import ViewModel

class PropertyGetRecorder:
    def __init__(self, view_model: ViewModel):
        self._view_model = view_model
        self._used_props = []
        self._recorders = {}

    def __getattribute__(self, prop):
        if prop in ['_view_model', '_used_props', '_recorders', 'get_used_properties']:
            return object.__getattribute__(self, prop)
        if self._view_model is not None:
            self._used_props.append(prop)
            value = getattr(self._view_model, prop)
            if isinstance(value, ViewModel):
                if value not in self._recorders:
                    self._recorders[value] = PropertyGetRecorder(value)
                value = self._recorders[value]
            return value

    def get_used_properties(self):
        used_props = {self._view_model: self._used_props}
        for recorder in self._recorders.values():
            used_props.update(recorder.get_used_properties())
        return used_props

class Binding:
    def __init__(self, instance, prop, modifier, expression: Expression):
        self._instance = instance
        self._expression = expression
        self.property = prop
        self.modifier = modifier
        self.dependencies = []

    def _init(self):
        parameters = self._get_record_parameters()()
        value = self.get_value(parameters)
        used_properties = self._get_used_properties(parameters)
        self._create_dependencies(used_properties)
        self.modifier(self._instance, self.property, value)

    def _get_record_parameters(self):
        parameters = self._expression.get_parameters()
        for key, value in parameters.items():
            if isinstance(value, ViewModel):
                parameters[key] = PropertyGetRecorder(value)
        return parameters

    def _get_used_properties(self, parameters):
        recorders = [value for value in parameters.values() \
                     if isinstance(value, PropertyGetRecorder)]
        used_properties = {}
        for recorder in recorders:
            for view_model, props in recorder.items():
                if view_model not in used_properties:
                    used_properties[view_model] = set()
                used_properties[view_model].update(props)

    def _create_dependencies(self, used_properties):
        for view_model, props in used_properties.items():
            for prop in props:
                view_model.observe(prop, self.update_callback)
                self.dependencies.append((view_model, prop))

    def get_value(self, parameters=None):
        return self._expression.compile(parameters)

    def update_callback(self, new_val, old_val):
        self.update_prop()

    def update_prop(self):
        self.modifier(self._instance, self.property, self.get_value())

    def destroy(self):
        for view_model, prop in self.dependencies:
            view_model.release_callback(prop, self.update_callback)
