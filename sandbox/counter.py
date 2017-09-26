from pyviews.observable.base import ViewModel

# pylint: disable=E1101
class Counter(ViewModel):
    def __init__(self):
        ViewModel.__init__(self)
        self.count = 0

    def up_count(self):
        self.count += 1
