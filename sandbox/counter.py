from viewmodel.base import ViewModel

class Counter(ViewModel):
    def __init__(self):
        ViewModel.__init__(self)
        self.count = 0

    @property
    def count(self):
        return self.__count

    @count.setter
    def count(self, val):
        self.__count = val
        self.notify('count')