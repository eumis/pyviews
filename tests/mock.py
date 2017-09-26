from pyviews.core.observable import Observable

class TestViewModel(Observable):
    def __init__(self, private, name, value):
        super().__init__()
        self._private = private
        self.name = name
        self.value = value

    def get_private(self):
        return self._private

class SomeObject:
    def __init__(self, one, two=None):
        self.one = one
        self.two = two
