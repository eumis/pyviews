from tkinter import StringVar

class Variable(StringVar):
    def __init__(self, convert=None):
        self._convert = convert
        StringVar.__init__(self)

    def get(self):
        value = super().get()
        if self._convert:
            value = self._convert(value)
        return value

def create_int_var(view_model, prop, default=None):
    convert = lambda value, default_=default: parse_int(value, default)
    var = Variable(convert)
    return create_var(view_model, prop, var)

def parse_int(value, default):
    try:
        return int(value)
    except ValueError:
        return default

def create_var(view_model, prop, var=None):
    var = var if var else Variable()
    apply_to_source_binding(var, view_model, prop)
    apply_to_view_binding(var, view_model, prop)
    return var


def apply_to_source_binding(var, view_model, prop):
    update_vm = lambda *args, v=view_model, a=prop, content=var: setattr(v, a, content.get())
    var.trace('w', update_vm)

def apply_to_view_binding(var, view_model, prop):
    update_view = lambda new_val, old_val, content=var: content.set(new_val)
    view_model.observe(prop, update_view)
    update_view(getattr(view_model, prop), None)
