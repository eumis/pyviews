from pyviews.core import Binding


class TwoWaysBinding(Binding):
    """Wrapper under two passed bindings"""

    def __init__(self, one: Binding, two: Binding):
        self._add_error_info = None
        self._one = one
        self._two = two
        super().__init__()

    @property
    def add_error_info(self):
        """Callback to add info to error"""
        return self._add_error_info

    @add_error_info.setter
    def add_error_info(self, value):
        self._add_error_info = value
        self._one.add_error_info = value
        self._two.add_error_info = value

    def bind(self):
        self.destroy()
        self._one.bind()
        self._two.bind()

    def destroy(self):
        self._one.destroy()
        self._two.destroy()
