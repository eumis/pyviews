from tkinter import StringVar

class Variable(StringVar):
    def __init__(self, convert=None):
        self._convert = convert
        StringVar.__init__(self)

    def get(self):
        value = StringVar.get(self)
        if self._convert:
            value = self._convert(value)
        return value

class StringBinding:
    def __init__(self, view_model, key):
        self._var = self._create_var()
        apply_to_source_binding(self._var, view_model, key)
        apply_to_view_binding(self._var, view_model, key)

    def _create_var(self):
        return Variable()

    def get_var(self):
        return self._var

def apply_to_source_binding(var, view_model, key):
    update_vm = lambda *args, v=view_model, a=key, content=var: setattr(v, a, content.get())
    var.trace('w', update_vm)

def apply_to_view_binding(var, view_model, key):
    update_view = lambda new_val, old_val, content=var: content.set(new_val)
    view_model.observe(key, update_view)
    update_view(getattr(view_model, key), None)

class IntBinding(StringBinding):
    def __init__(self, view_model, key, default=None):
        self._default = default
        StringBinding.__init__(self, view_model, key)

    def _create_var(self):
        convert = lambda value, default=self._default: parse_int(value, default)
        return Variable(convert)

def parse_int(value, default):
    try:
        return int(value)
    except ValueError:
        return default
