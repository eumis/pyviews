from sys import exc_info

from pyviews.core import Binding, BindingTarget
from pyviews.core import Observable
from pyviews.core import ViewsError, BindingError


class ObservableBinding(Binding):
    """Binds to observable property"""

    def __init__(self, on_update: BindingTarget, observable: Observable, prop):
        super().__init__()
        self._on_update = on_update
        self._observable = observable
        self._prop = prop

    def bind(self):
        self.destroy()
        self._observable.observe(self._prop, self._update_callback)
        self._update_target(getattr(self._observable, self._prop))

    def _update_callback(self, new_val, _):
        try:
            self._update_target(new_val)
        except ViewsError as error:
            self.add_error_info(error)
            raise
        except BaseException:
            info = exc_info()
            error = BindingError(BindingError.TargetUpdateError)
            self.add_error_info(error)
            error.add_cause(info[1])
            raise error from info[1]

    def _update_target(self, value):
        self._on_update(value)

    def destroy(self):
        self._observable.release(self._prop, self._update_callback)
