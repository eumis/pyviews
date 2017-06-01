from pyviews.viewmodel.base import ViewModel

# pylint: disable=E1101
class Counter(ViewModel):
    def __init__(self):
        ViewModel.__init__(self)
        self.define_prop('count', 0)

    def up_count(self):
        self.count += 1
