from viewmodel.base import ViewModel

class Counter(ViewModel):
    def __init__(self):
        ViewModel.__init__(self)
        self.__count = 0

    @property
    def count(self):
        return self.__count

    @count.setter
    def count(self, val):
        old = self.__count
        self.__count = val
        self.notify('count', val, old)

    def up_count(self):
        self.count += 1
