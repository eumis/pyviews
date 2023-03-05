"""Two ways binding"""

from pyviews.core.binding import Binding


class TwoWaysBinding(Binding):
    """Wrapper under two passed bindings"""

    def __init__(self, one: Binding, two: Binding):
        self._one = one
        self._two = two
        super().__init__()

    def bind(self):
        self.destroy()
        self._one.bind()
        self._two.bind()

    def destroy(self):
        self._one.destroy()
        self._two.destroy()
