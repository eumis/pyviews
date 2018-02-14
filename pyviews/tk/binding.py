'''Bindings specific for tkinter'''

from tkinter import Variable
from pyviews.core.binding import Binding, BindingTarget

class VariableTarget(BindingTarget):
    '''Target is tkinter Var'''
    def __init__(self, var: Variable):
        self._var = var

    def on_change(self, value):
        self._var.set(value)

class VariableBinding(Binding):
    '''Binding is subscribed on tkinter Var changes'''
    def __init__(self, target: BindingTarget, var: Variable, converter=None):
        self._target = target
        self._var = var
        self._converter = converter
        self._trace_id = None

    def bind(self):
        self.destroy()
        self._trace_id = self._var.trace_add('write', self._callback)

    def _callback(self, *args):
        value = self._var.get()
        if self._converter:
            value = self._converter(value)
        self._target.on_change(value)

    def destroy(self):
        if self._trace_id:
            self._var.trace_vdelete(self._trace_id)
        self._trace_id = None
