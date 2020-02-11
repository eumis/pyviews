"""Observable binding"""

from pyviews.core import Binding, BindingCallback
from pyviews.core import Observable
from pyviews.core import BindingError
from pyviews.core.error import error_handling


class ObservableBinding(Binding):
    """Binds to observable property"""

    def __init__(self, callback: BindingCallback, observable: Observable, observable_property: str):
        super().__init__()
        self._callback = callback
        self._observable = observable
        self._property = observable_property

    def bind(self):
        self.destroy()
        self._observable.observe(self._property, self._update_callback)
        self._callback(getattr(self._observable, self._property))

    def _update_callback(self, new_val, _):
        with error_handling(BindingError(BindingError.BindingCallbackError), self.add_error_info):
            self._callback(new_val)

    def destroy(self):
        self._observable.release(self._property, self._update_callback)
