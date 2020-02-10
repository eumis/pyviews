from sys import exc_info

from pyviews.core import Binding, BindingCallback
from pyviews.core import Observable
from pyviews.core import ViewsError, BindingError


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
        try:
            self._callback(new_val)
        except ViewsError as error:
            self.add_error_info(error)
            raise
        except BaseException:
            info = exc_info()
            error = BindingError(BindingError.TargetUpdateError)
            self.add_error_info(error)
            error.add_cause(info[1])
            raise error from info[1]

    def destroy(self):
        self._observable.release(self._property, self._update_callback)
