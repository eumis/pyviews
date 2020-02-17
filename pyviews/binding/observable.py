"""Observable binding"""

from pyviews.core import Binding, BindingCallback, BindingError, PyViewsError
from pyviews.core import Observable, error_handling


class ObservableBinding(Binding):
    """Binds to observable property"""

    def __init__(self, callback: BindingCallback, observable: Observable, observable_property: str):
        super().__init__()
        self._callback = callback
        self._observable = observable
        self._property = observable_property

    def bind(self):
        self.destroy()
        self._observable.observe(self._property, self._execute_callback)
        self._execute_callback(getattr(self._observable, self._property), None)

    def _execute_callback(self, value, _):
        with error_handling(BindingError, self._add_error_info):
            self._callback(value)

    def _add_error_info(self, error: PyViewsError):
        error.add_info('Binding', self)
        error.add_info('Binding observable', self._observable)
        error.add_info('Binding property', self._property)
        error.add_info('Binding callback', self._callback)

    def destroy(self):
        self._observable.release(self._property, self._execute_callback)
